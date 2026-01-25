#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <filesystem>
#include "../include/Autel_IrTempParser.h"
#include <opencv2/opencv.hpp>

namespace fs = std::filesystem;

bool processImage(const std::string& inputPath, const std::string& outputPath, int w = 640, int h = 512) {
    TempStatInfo tempStatInfo;
    std::map<std::string, Autel_IR_INFO_S> metadata;
    std::vector<std::vector<float>> tempArray;

    int ret = GetIrPhotoTempInfo(inputPath.c_str(), w, h, tempStatInfo, metadata, tempArray);
    if (ret != 0) {
        std::cerr << "❌ Failed to parse: " << inputPath << "\n";
        return false;
    }

    // Convert to OpenCV Mat (32F = 32-bit float)
    cv::Mat tempMat(h, w, CV_32F);
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            tempMat.at<float>(y, x) = tempArray[y][x];
        }
    }

    // Save as TIFF
    if (!cv::imwrite(outputPath, tempMat)) {
        std::cerr << "❌ Failed to write TIFF: " << outputPath << "\n";
        return false;
    }

    std::cout << "✅ Saved: " << outputPath 
              << " (max=" << tempStatInfo.max << "°C)\n";
    return true;
}

int main(int argc, char* argv[]) {
    std::string inputDir = "../images";
    std::string outputDir = "../output_tifs";

    if (argc >= 2) inputDir = argv[1];
    if (argc >= 3) outputDir = argv[2];

    fs::create_directories(outputDir);

    int successCount = 0;
    for (const auto& entry : fs::directory_iterator(inputDir)) {
        auto path = entry.path();
        std::string ext = path.extension().string();
        // Case-insensitive check
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);

        if (ext == ".jpg" || ext == ".jpeg") {
            std::string stem = path.stem().string();
            std::string outputPath = (fs::path(outputDir) / (stem + ".tif")).string();
            if (processImage(path.string(), outputPath)) {
                successCount++;
            }
        }
    }

    std::cout << "\n🎉 Processed " << successCount << " images.\n";
    return 0;
}