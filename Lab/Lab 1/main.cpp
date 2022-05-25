#include <iostream>
#include <stdlib.h>
#include <math.h>

using namespace std;

int main() {
	

	// generating 1000 exponential random variables
	// created variables for lambda, exp variables, numerands, mean and variance
	// created a seed from the random time library
	const int lambda = 75;
	const int num_test_exp_rand_var = 1000;
	int run = 1;
	double mean_numerator = 0.00;
	double exp_rand_var = 0.00;
	double summation_variance = 0.00;
	double save_summation_variance[1000];
	double mean = 0.00;
	srand( (unsigned)time( NULL ) );

	cout << "Generating 1000 exponential random variables: " << endl;
	
	// simple algo for generating 1000 exponential random variables
	// also saving to array for variance calculation
	for (int i = 0; i < num_test_exp_rand_var; i++) {
		exp_rand_var = -(log(1-((float) rand() / RAND_MAX)) / lambda);
		mean_numerator += exp_rand_var;
		save_summation_variance[i] = exp_rand_var;
		cout << "Run #" << run << ": x = " << exp_rand_var << endl;
		run++;
	}	

	// calculating mean and outputting result
	mean = mean_numerator / num_test_exp_rand_var;
	cout << "Mean of exponential random variables: " << mean << endl;
	
	// calculating summation of random variables - mean squared / number of test exp random var - 1 and outputting result
	for (int j = 0; j < num_test_exp_rand_var; j++) {
		summation_variance += pow(2, (save_summation_variance[j] - mean));
	}
	cout << "Variance: " << summation_variance / (num_test_exp_rand_var - 1) << endl;
    
}

/*
	Created run temp variables to debug why the simulate function only runs for some rho values
	Added simple cout messages to find which function is the one that is stopping the process
	Currently looking into the event function
	*/