/*
Author: Michael Moss
Contact: mikejmoss3@gmail.com
Last Edited: 2021-08-30

Header file for ShellDist.cpp class

*/

// Ensure that C++ doesn't have any problems if this header is accessed by multiple scripts simultaneously
#ifndef SHELLDISTCLASS_H
#define SHELLDISTCLASS_H

// Import Standard Libraries
#include <cmath>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>

// Import Custom Libraries
#include "cosmology.hpp"
#include "utilfuncs.hpp"

using namespace std;

// Declare light curve class
class ShellDist
{
public:
	// Class constructor 
	ShellDist(int numshells=5000, double E_dot=1e52);

	// Class member variables
	int numshells; // Number of shells in the jet
	double E_dot; // Injection energy from the central engine
	std::vector<double> shell_radius; // Records shell radius 
	std::vector<double> shell_gamma; // Records shell Lorentz factor
	std::vector<double> shell_mass; // Records shell mass 
	std::vector<float> shell_te; // Records launch time of the shells
	std::vector<int> shell_status; // Status indicator: 0 = deactived, 1 = active and launched, 2 = not launched

	// Class member functions
	// Distribute the shells according to a step function with initial Lorentz factor G1 and secondary Lorentz factor G2
	// The step occurs when the cumulative mass of the shells reaches a fraction of the total mass specified by mfrac
	void step(float dte, float g1=100, float g2=400, float mfrac=0.5, bool fluctuations = false);
	// The smooth step occurs when the cumulative mass of the shells reaches a fraction of the total mass specified by mfrac
	void smoothstep(float dte, float g1=100, float g2=400, float mfrac=0.5, bool fluctuations = false);
	// Distribute the shell according to an oscillatory function described in Hascoet et al. 2013. 
	void oscillatory(float dte, float median=333., float amp=2./3., float freq=5., float decay=0.5, bool fluctuations = false);

	// Distribute the shells by injecting Gaussians at specific places. 
	void gauss_inject(float dte, float gamma_ave = 1.1, float decay = 0.5, int num_gauss = 2, std::vector<float> means = {1, 7}, std::vector<float> amps = {100, 50}, std::vector<float> sigmas = {10, 10}, std::vector<float> sigma_count = {3., 3.}, bool fluctuations = false);
	// Distribute the shells by injecting Squares at specific places. 
	void square_inject(float dte, float gamma_ave = 1.1, float decay = 0.5, int num_squares = 2, std::vector<float> starts = {1, 7}, std::vector<float> durations = {50, 50} , std::vector<float> amps = {100, 50}, bool fluctuations = false);
	// Distribute the shells by injecting FREDs at specific places. 
	void fred_inject(float dte, float gamma_ave = 1.1, float decay = 0.5, int num_freds = 2, std::vector<float> starts = {1, 7}, std::vector<float> tau_1s = { 1, 1}, std::vector<float> tau_2s = {4.5, 4.5}, std::vector<float> amps = {200, 50}, bool fluctuations = false);
	// Make a linear distribution
	void linear(float dte, float g1 = 500., float g2 = 1., bool fluctuations = false);


	// Write shell distribution to a text file
	void WriteToTXT(string filename, double time = 0., bool append=false);

};

#endif 