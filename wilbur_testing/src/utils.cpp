#include <chrono>
#include <iomanip>
#include <sstream>
#include <string>

std::string generate_timestamp_filename(const std::string& base, const std::string& ext) {
    // Get the current system time
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);

    // Format the time as YYYYMMDD_HHMMSS
    std::stringstream ss;
    ss << base << std::put_time(std::localtime(&in_time_t), "%Y%m%d_%H%M%S") << "." << ext;
    
    return ss.str();
}