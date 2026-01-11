#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <cmath>
#include <algorithm>
#include <filesystem>
#include "../include/Autel_IrTempParser.h"
#include "../include/nlohmann/json.hpp"
#include <opencv2/opencv.hpp>

using json = nlohmann::json;

#define DLLEXPORT extern "C" __declspec(dllexport)

// Helper to sanitize float values
float sanitizeTemp(float val) {
    if (std::isnan(val) || std::isinf(val) || val >= 60000.0f) {
        return -273.15f; // Error value (absolute zero approx)
    }
    return val;
}

// Core processing logic
DLLEXPORT int ConvertToTiff(const char* inputPath, const char* outputPath) {
    std::string inFile(inputPath);
    std::string outFile(outputPath);
    int w = 640;
    int h = 512;

    // 1. Load RGB Image
    cv::Mat rgbImage = cv::imread(inFile, cv::IMREAD_COLOR);
    if (rgbImage.empty()) return -1; // Error: Image not found

    // Resize if needed
    if (rgbImage.cols != w || rgbImage.rows != h) {
        cv::resize(rgbImage, rgbImage, cv::Size(w, h));
    }

    // 2. Get Thermal Data
    TempStatInfo tempStatInfo;
    std::map<std::string, Autel_IR_INFO_S> metadata;
    std::vector<std::vector<float>> tempArray;

    int ret = GetIrPhotoTempInfo(inFile.c_str(), w, h, tempStatInfo, metadata, tempArray);
    if (ret != 0) return -2; // Error: SDK failed

    // 3. Create 16-bit Thermal Band
    cv::Mat thermalBand(h, w, CV_16U);
    
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            float tempVal = sanitizeTemp(tempArray[y][x]);
            
            // Formula: (Temp * 100) + 10000
            // Example: 23.45 -> 2345 + 10000 = 12345
            // Example: -5.00 -> -500 + 10000 = 9500
            float encodedFloat = (tempVal * 100.0f) + 10000.0f;
            
            // Clamp to uint16 range (0 - 65535) just in case
            encodedFloat = std::max(0.0f, std::min(65535.0f, encodedFloat));
            
            thermalBand.at<uint16_t>(y, x) = static_cast<uint16_t>(encodedFloat + 0.5f);
        }
    }

    // 4. Process RGB Bands (Scale 8-bit to 16-bit)
    std::vector<cv::Mat> rgbChannels;
    cv::split(rgbImage, rgbChannels);
    std::vector<cv::Mat> outputChannels;

    for (int i = 0; i < 3; ++i) {
        cv::Mat channel16;
        rgbChannels[i].convertTo(channel16, CV_16U, 257.0); // 0-255 -> 0-65535
        outputChannels.push_back(channel16);
    }
    
    // Add Thermal as 4th band
    outputChannels.push_back(thermalBand);

    // 5. Merge and Save
    cv::Mat output4Channel;
    cv::merge(outputChannels, output4Channel);
    
    if (!cv::imwrite(outFile, output4Channel)) return -3; // Error: Write failed

    return 0; // Success
}

DLLEXPORT int GetMetadataJSON(const char* inputPath, char* buffer, int bufferLen) {
    std::string inFile(inputPath);
    int w = 640;
    int h = 512;

    TempStatInfo tempStatInfo;
    std::map<std::string, Autel_IR_INFO_S> metadata;
    std::vector<std::vector<float>> tempArray;

    int ret = GetIrPhotoTempInfo(inFile.c_str(), w, h, tempStatInfo, metadata, tempArray);
    if (ret != 0) return -1;

    json j;
    j["stats"] = {
        {"min", tempStatInfo.min},
        {"max", tempStatInfo.max},
        {"avg", tempStatInfo.avg},
        {"min_point", {{"x", tempStatInfo.minPoint.x}, {"y", tempStatInfo.minPoint.y}}},
        {"max_point", {{"x", tempStatInfo.maxPoint.x}, {"y", tempStatInfo.maxPoint.y}}}
    };

    // Extract Autel proprietary metadata
    json meta_j;
    for (auto const& [key, val] : metadata) {
        // Try to determine if it's a number or string based on value
        if (std::string(val.show_value) != "NA") {
             meta_j[key] = val.show_value;
        } else {
             meta_j[key] = val.num_value;
        }
    }
    j["metadata"] = meta_j;

    std::string jsonStr = j.dump();
    
    // Copy to buffer
    if (jsonStr.length() + 1 > bufferLen) return -2; // Buffer too small
    
    strcpy_s(buffer, bufferLen, jsonStr.c_str());
    
    return 0;
}
