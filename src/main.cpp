#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <string>
#include "../include/Autel_IrTempParser.h"
#include "../include/nlohmann/json.hpp"

using json = nlohmann::json;

int main() {
    const char* imagePath = "../images/IRX_4552.JPG";
    int w = 640;
    int h = 512;

    TempStatInfo tempStatInfo;
    std::map<std::string, Autel_IR_INFO_S> metadata;
    std::vector<std::vector<float>> tempArray;

    std::cout << "🔍 Parsing: " << imagePath << std::endl;

    int ret = GetIrPhotoTempInfo(imagePath, w, h, tempStatInfo, metadata, tempArray);

    if (ret != 0) {
        std::cerr << "❌ GetIrPhotoTempInfo failed (returned " << ret << ")" << std::endl;
        return -1;
    }

    std::cout << "✅ Parsed successfully. Stats: max=" << tempStatInfo.max 
              << "°C, min=" << tempStatInfo.min << "°C" << std::endl;

    // Build JSON
    json output;
    output["statistics"] = {
        {"max_temp", tempStatInfo.max},
        {"min_temp", tempStatInfo.min},
        {"avg_temp", tempStatInfo.avg},
        {"max_point", {{"x", tempStatInfo.maxPoint.x}, {"y", tempStatInfo.maxPoint.y}}},
        {"min_point", {{"x", tempStatInfo.minPoint.x}, {"y", tempStatInfo.minPoint.y}}}
    };

    // json metaJson;
    // for (const auto& pair : metadata) {
    //     const std::string& key = pair.first;
    //     const Autel_IR_INFO_S& info = pair.second;
    //     metaJson[key] = {
    //         {"tag", info.tag},
    //         {"len", info.len},
    //         {"show_value", info.show_value},
    //         {"str_value", std::string(info.str_value)},
    //         {"num_value", info.num_value}
    //     };
    // }
    // output["metadata"] = metaJson;

    // Write to file
    std::string outFile = "output.json";
    std::ofstream f(outFile);
    if (!f.is_open()) {
        std::cerr << "❌ Failed to open " << outFile << " for writing!" << std::endl;
        return -1;
    }

    f << std::setw(2) << output << std::endl;
    f.close();

    std::cout << "✅ Saved to: " << outFile << std::endl;
    return 0;
}