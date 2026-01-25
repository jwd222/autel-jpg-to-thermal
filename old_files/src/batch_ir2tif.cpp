#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <filesystem>
#include <algorithm>
#include <cmath>
#include <fstream>
#include "../include/Autel_IrTempParser.h"
#include <opencv2/opencv.hpp>

namespace fs = std::filesystem;

// 🔥 SET YOUR GLOBAL TEMPERATURE RANGE HERE (in °C)
const float GLOBAL_TEMP_MIN = 12.80f;
const float GLOBAL_TEMP_MAX = 138.70f;
const float INVALID_THRESHOLD = 65000.0f;

bool processImage(const std::string& inputPath, const std::string& outputPath, int w = 640, int h = 512) {
    // Load original RGB image
    cv::Mat rgbImage = cv::imread(inputPath, cv::IMREAD_COLOR);
    if (rgbImage.empty()) {
        std::cerr << "❌ Failed to load RGB image: " << inputPath << "\n";
        return false;
    }

    // Resize if dimensions don't match thermal data
    if (rgbImage.cols != w || rgbImage.rows != h) {
        cv::resize(rgbImage, rgbImage, cv::Size(w, h));
        std::cout << "ℹ️  Resized RGB to match thermal dimensions: " << w << "x" << h << "\n";
    }

    // Parse thermal data
    TempStatInfo tempStatInfo;
    std::map<std::string, Autel_IR_INFO_S> metadata;
    std::vector<std::vector<float>> tempArray;

    int ret = GetIrPhotoTempInfo(inputPath.c_str(), w, h, tempStatInfo, metadata, tempArray);
    if (ret != 0) {
        std::cerr << "❌ Failed to parse thermal data: " << inputPath << "\n";
        return false;
    }

    std::cout << "📸 SDK stats: min=" << tempStatInfo.min
              << "°C, max=" << tempStatInfo.max
              << "°C, avg=" << tempStatInfo.avg << "°C\n";

    // Create 16-bit thermal band
    cv::Mat thermalBand(h, w, CV_16U);
    const float tempRange = GLOBAL_TEMP_MAX - GLOBAL_TEMP_MIN;

    if (tempRange <= 0.0f) {
        std::cerr << "❌ Invalid global temperature range!\n";
        return false;
    }

    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            float tempVal = tempArray[y][x];

            // 🛡️ Filter out sentinel/invalid values
            if (std::isnan(tempVal) || std::isinf(tempVal) || tempVal >= INVALID_THRESHOLD) {
                tempVal = GLOBAL_TEMP_MIN;
            }

            // Clamp to global valid range
            tempVal = std::max(GLOBAL_TEMP_MIN, std::min(GLOBAL_TEMP_MAX, tempVal));

            // Scale to 0–65535 (16-bit)
            uint16_t scaled = static_cast<uint16_t>(
                ((tempVal - GLOBAL_TEMP_MIN) / tempRange) * 65535.0f + 0.5f
            );
            thermalBand.at<uint16_t>(y, x) = scaled;
        }
    }

    // Convert RGB bands to 16-bit (scale from 0-255 to 0-65535)
    std::vector<cv::Mat> rgbChannels;
    cv::split(rgbImage, rgbChannels);
    
    std::vector<cv::Mat> outputChannels;
    for (int i = 0; i < 3; ++i) {
        cv::Mat channel16;
        rgbChannels[i].convertTo(channel16, CV_16U, 257.0); // 257 = 65535/255
        outputChannels.push_back(channel16);
    }
    
    // Add thermal band as 4th channel
    outputChannels.push_back(thermalBand);

    // Merge all 4 channels
    cv::Mat output4Channel;
    cv::merge(outputChannels, output4Channel);

    // Save as 16-bit 4-channel TIFF
    if (!cv::imwrite(outputPath, output4Channel)) {
        std::cerr << "❌ Failed to write TIFF: " << outputPath << "\n";
        return false;
    }

    std::cout << "✅ Saved 4-channel TIFF (RGB + Thermal): " << outputPath << "\n";
    return true;
}

int main(int argc, char* argv[]) {
    std::string inputDir = "../images";
    std::string outputDir = "../output_tifs";

    if (argc >= 2) inputDir = argv[1];
    if (argc >= 3) outputDir = argv[2];

    fs::create_directories(outputDir);

    int successCount = 0;
    int totalCount = 0;

    for (const auto& entry : fs::directory_iterator(inputDir)) {
        auto path = entry.path();
        std::string ext = path.extension().string();
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);

        if (ext == ".jpg" || ext == ".jpeg") {
            totalCount++;
            std::string stem = path.stem().string();
            std::string outputPath = (fs::path(outputDir) / (stem + ".tif")).string();

            std::cout << "\n[" << totalCount << "] Processing: " << path.filename().string() << "\n";
            if (processImage(path.string(), outputPath)) {
                successCount++;
            }
        }
    }

    // Print summary to console
    std::cout << "\n🎉 Conversion complete!\n";
    std::cout << "   Total JPGs: " << totalCount << "\n";
    std::cout << "   Success:    " << successCount << "\n";
    std::cout << "   Global temp range: " << GLOBAL_TEMP_MIN << "°C – " << GLOBAL_TEMP_MAX << "°C\n";
    std::cout << "\n📝 To convert back to Celsius: temp_celsius = (band4_value / 65535.0) * " 
              << (GLOBAL_TEMP_MAX - GLOBAL_TEMP_MIN) << " + " << GLOBAL_TEMP_MIN << "\n";

    // Save summary to text file
    std::string summaryPath = (fs::path(outputDir) / "conversion_info.txt").string();
    std::ofstream summaryFile(summaryPath);
    
    if (summaryFile.is_open()) {
        summaryFile << "=================================================\n";
        summaryFile << "   THERMAL IMAGE CONVERSION SUMMARY\n";
        summaryFile << "=================================================\n\n";
        summaryFile << "Total JPG images processed: " << totalCount << "\n";
        summaryFile << "Successfully converted:     " << successCount << "\n";
        summaryFile << "Failed:                     " << (totalCount - successCount) << "\n\n";
        summaryFile << "=================================================\n";
        summaryFile << "   TEMPERATURE ENCODING INFORMATION\n";
        summaryFile << "=================================================\n\n";
        summaryFile << "Global temperature range: " << GLOBAL_TEMP_MIN << "°C to " 
                    << GLOBAL_TEMP_MAX << "°C\n\n";
        summaryFile << "Output format: 4-channel 16-bit TIFF\n";
        summaryFile << "  - Band 1-3: RGB (original image data)\n";
        summaryFile << "  - Band 4:   Temperature (encoded as 16-bit integer)\n\n";
        summaryFile << "=================================================\n";
        summaryFile << "   HOW TO DECODE TEMPERATURE (Band 4)\n";
        summaryFile << "=================================================\n\n";
        summaryFile << "To convert Band 4 values back to Celsius:\n\n";
        summaryFile << "temp_celsius = (band4_value / 65535.0) * " 
                    << (GLOBAL_TEMP_MAX - GLOBAL_TEMP_MIN) << " + " << GLOBAL_TEMP_MIN << "\n\n";
        summaryFile << "Example calculations:\n";
        summaryFile << "  - band4_value = 0     → " << GLOBAL_TEMP_MIN << "°C\n";
        summaryFile << "  - band4_value = 32768 → " 
                    << (32768.0 / 65535.0 * (GLOBAL_TEMP_MAX - GLOBAL_TEMP_MIN) + GLOBAL_TEMP_MIN) 
                    << "°C\n";
        summaryFile << "  - band4_value = 65535 → " << GLOBAL_TEMP_MAX << "°C\n\n";
        summaryFile << "=================================================\n";
        
        summaryFile.close();
        std::cout << "\n💾 Summary saved to: " << summaryPath << "\n";
    } else {
        std::cerr << "⚠️  Warning: Could not create summary file: " << summaryPath << "\n";
    }

    return 0;
}