#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <sstream>
#include <iterator>
#include <algorithm>
#include <stdexcept>
#include <iomanip>
#include <tuple>

#include "DataFrame.h"

DataFrame::DataFrame() {
    isEmpty = true;
}

DataFrame::DataFrame(std::vector<std::string> colNames, std::map<std::string, std::vector<std::string>> elements) {
	fColumnNames = colNames;
	fElements = elements;
}

DataFrame DataFrame::fromCsv(std::string path, std::string delimiter) {
	// parse csv mapping file
	std::string csvLine, token;
	std::ifstream csvFile(path);
	std::vector<std::string> mappingRow;

	std::vector<std::string> colNames;
	std::map<std::string, std::vector<std::string>> elements;
    
	if (!csvFile.is_open())
		throw std::invalid_argument("Could not open file "+path);
	for (int lineIndex=0; getline(csvFile, csvLine); lineIndex++) {
		mappingRow.clear();

		std::stringstream lineStream(csvLine);

		// split line by separator
        size_t pos = 0;
        while ((pos = csvLine.find(delimiter)) != std::string::npos) {
            token = csvLine.substr(0, pos);
            csvLine.erase(0, pos + delimiter.length());
            mappingRow.push_back(token);
        }
        mappingRow.push_back(csvLine);

		if (lineIndex==0) { // parse header
			colNames = mappingRow;
		} else { // parse mapping row
			for (int icol=0; icol<mappingRow.size(); icol++) {
				// in case of generic class:
				// std::stringstream convertToT(mappingRow[icol]);
				// T value;
				// convertToT >> value;
				// fElements[colNames[icol]].push_back(value);
				elements[colNames[icol]].push_back(mappingRow[icol]);
			}
		}
	}
	csvFile.close();
	return DataFrame(colNames, elements);
}

std::string DataFrame::getElement(std::string column, int row) {
    if (fElements.count(column)>0) {
        return fElements[column][row];
    } else {
        throw std::out_of_range(std::string("Column '" + column + "' does not exist in dataframe"));
    }
}

void DataFrame::print() {
	for (auto colName:fColumnNames) std::cout << std::setw(10) << colName << "\t";
	std::cout << std::endl;

	int minRows = getNRows();
	if (minRows>10) minRows = 10;
	for (int irow=0; irow<minRows; irow++) {
		for (auto colName:fColumnNames) std::cout << std::setw(10) << fElements[colName][irow] << "\t";
		std::cout << std::endl;
	}
}

bool DataFrame::contains(std::vector<std::string> values) {
    bool doesContain = true;
    for (int irow=0; irow<getNRows(); irow++) {

        /*std::cout << "Comparing ";
        for (std::string val:values) std::cout << val << " ";
        std::cout << " with ";
        for (std::string colname : fColumnNames) std::cout << getElement(colname, irow) << " ";
        std::cout << "...";*/

        doesContain = true;
        for (int icol=0; icol<fColumnNames.size(); icol++) {
            std::string colName = fColumnNames.at(icol);
            if (getElement(colName, irow) != values.at(icol)) {
                doesContain = false; // at least one key is different
                break; // don't scan the other columns for this row
            }
        }
        //std::cout << " contains: " << doesContain << std::endl;
        // if one row matches, don't scan the other rows and return true:
        if (doesContain) return doesContain;
    }
    return doesContain;
}
