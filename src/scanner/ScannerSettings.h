#pragma once

#include "Asset.h"

/**
 * @brief Scanner settings class
 */
class ScannerSettings : public Asset {

public:
    // ***  ATTRIBUTES  *** //
    // ******************** //
    /**
     * @brief Flag to specify if scanner is active (true) or not (false)
     *
     * When a scanner is not active, no points will be captured
     */
	bool active = true;
	/**
	 * @brief Beam sample quality
	 */
	int beamSampleQuality = 5;
	/**
	 * @brief Amount of rotation (radians) per second for the scanner head
	 */
	double headRotatePerSec_rad = 0;
	/**
	 * @brief Starting angle (radians) for the scanner head
	 */
	double headRotateStart_rad = 0;
	/**
	 * @brief Ending angle (radians) for the scanner head
	 */
	double headRotateStop_rad = 0;
	/**
	 * @brief Pulse frequency (hertz)
	 */
	int pulseFreq_Hz = 0;
	/**
	 * @brief Scan angle (radians)
	 */
	double scanAngle_rad = 0;
	/**
	 * @brief Minimum vertical angle (radians)
	 */
    double verticalAngleMin_rad = 0;
    /**
     * @brief Maximum vertical angle (radians)
     */
    double verticalAngleMax_rad = 0;
    /**
     * @brief Scanning frequency (hertz)
     */
	int scanFreq_Hz = 0;
	/**
	 * @brief Beam divergence angle (radians)
	 */
	double beamDivAngle = 0.003;
	/**
	 * @brief Pulse length (nanoseconds)
	 */
	double pulseLength_ns = 0;
	/**
	 * @brief Time interval between trajectory recollections (seconds)
	 */
	double trajectoryTimeInterval = 0.0; // In seconds

	// ***  CONSTRUCTION / DESTRUCTION  *** //
	// ************************************ //
	/**
	 * @brief Scanner settings default constructor
	 */
	ScannerSettings() = default;

	//Copy constructor:
	ScannerSettings(ScannerSettings* other) {
		if (other == NULL) return;

		this->active = other->active;
		this->beamSampleQuality = other->beamSampleQuality;
		this->headRotatePerSec_rad = other->headRotatePerSec_rad;
		this->headRotateStart_rad = other->headRotateStart_rad;
		this->headRotateStop_rad = other->headRotateStop_rad;
		this->pulseFreq_Hz = other->pulseFreq_Hz;
		this->scanAngle_rad = other->scanAngle_rad;
		this->scanFreq_Hz = other->scanFreq_Hz;
		this->beamDivAngle = other->beamDivAngle;
		this->pulseLength_ns = other->pulseLength_ns;
	}
};