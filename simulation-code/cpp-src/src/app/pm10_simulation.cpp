#include <mpi.h>
#include <omp.h>
#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <numeric>
#include <algorithm>

void write_global_average_to_file(double global_avg, const std::string& filepath) {
    std::ofstream results_file(filepath, std::ios_base::app); // Append to the file
    if (!results_file) {
        std::cerr << "Error opening results file: " << filepath << std::endl;
        return;
    }
    results_file << "Global Average PM10 Concentration: " << global_avg << std::endl;
}

// Function to check for high PM10 concentration and alert
void alert_high_pm10_concentration(double global_avg, double threshold = 30.0) {
    if (global_avg > threshold) {
        std::cout << "Alert: High PM10 concentration detected: " << global_avg << std::endl;
    }
}
// Function to read PM10 data from a CSV file
std::vector<double> read_pm10_data(const std::string& filepath, int targetColumn) {
    std::vector<double> pm10Values;
    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filepath << std::endl;
        return pm10Values;
    }

    std::string line;
    std::getline(file, line); // Skip header
    while (std::getline(file, line)) {
        std::stringstream linestream(line);
        std::string cell;
        double value;
        int column = 0;
        while (std::getline(linestream, cell, ',')) {
            if (column == targetColumn) {
                try {
                    value = std::stod(cell);
                    pm10Values.push_back(value);
                } catch (const std::invalid_argument& ia) {
                    std::cerr << "Warning: Could not convert value to double: " << cell << std::endl;
                }
                break;
            }
            ++column;
        }
    }
    return pm10Values;
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);

    int world_size, world_rank;
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

    MPI_Comm shm_comm;
    MPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, 0, MPI_INFO_NULL, &shm_comm);
    int shm_rank, shm_size;
    MPI_Comm_rank(shm_comm, &shm_rank);
    MPI_Comm_size(shm_comm, &shm_size);

    MPI_Win shm_win;
    double* shm_data_ptr = nullptr;
    int totalSize = 0;

    if (shm_rank == 0) {
        std::vector<double> allData;
        if (world_rank == 0) {
            int targetColumn = 17;
            allData = read_pm10_data("preprocessed_for_cpp.csv", targetColumn);
            totalSize = allData.size();
            std::cout << "Total data size: " << totalSize << std::endl;
        }
        MPI_Bcast(&totalSize, 1, MPI_INT, 0, MPI_COMM_WORLD);
        MPI_Win_allocate_shared(totalSize * sizeof(double), sizeof(double), MPI_INFO_NULL, shm_comm, &shm_data_ptr, &shm_win);
        if (world_rank == 0) {
            std::copy(allData.begin(), allData.end(), shm_data_ptr);
        }
    } else {
        MPI_Bcast(&totalSize, 1, MPI_INT, 0, MPI_COMM_WORLD);
        MPI_Aint shm_size;
        int disp_unit;
        MPI_Win_allocate_shared(0, sizeof(double), MPI_INFO_NULL, shm_comm, &shm_data_ptr, &shm_win);
        MPI_Win_shared_query(shm_win, 0, &shm_size, &disp_unit, &shm_data_ptr);
    }

    MPI_Win_fence(0, shm_win);

    // Directly access shm_data_ptr for reading and processing data
    int local_start = totalSize * world_rank / world_size;
    int local_end = totalSize * (world_rank + 1) / world_size;
    double local_sum = 0.0;
    int local_count = local_end - local_start;

    #pragma omp parallel for reduction(+:local_sum) schedule(dynamic)
    for (int i = local_start; i < local_end; ++i) {
        local_sum += shm_data_ptr[i];
    }
    double local_avg = local_count > 0 ? local_sum / local_count : 0;
    std::cout << "Process " << world_rank << " Local Average: " << local_avg << std::endl;

    double global_sum = 0.0;
    int global_count = 0;
    MPI_Reduce(&local_sum, &global_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
    MPI_Reduce(&local_count, &global_count, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);

    if (world_rank == 0) {
        double global_avg = global_count > 0 ? global_sum / global_count : 0;
        std::cout << "Global Average PM10 Concentration: " << global_avg << std::endl;
        
        write_global_average_to_file(global_avg, "pm10_analysis_results.txt");

        alert_high_pm10_concentration(global_avg);
    }

    MPI_Win_free(&shm_win);
    MPI_Comm_free(&shm_comm);
    MPI_Finalize();
    return 0;
}
