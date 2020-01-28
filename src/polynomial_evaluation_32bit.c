/*
  This file contains two implementation for polynomial evaluation modulo some
  number.

  * PolynomialEvaluation() is the naive version which does not require
  additional inputs or precomputation and works for any modulus.
  * PolynomialEvaluation2() uses Montgomery representation in the implementation
  (the inputs are still in standard form), and works only for odd modulus.

  All implementations are written with uint32_t. They should be refactored to
  work with 256-bit integers, using a library that supports multiplying two
  256-bit integers with a 512-bit result.
*/


#include "ewasm.h"







/*
  Computes the evaluation of the polynomial:
    f(x) = coefs[0] + coefs[1] * x + coefs[2] * x^2 + ...
  on the given point, modulo the given modulus.
*/
uint32_t PolynomialEvaluation(uint32_t coefs[], uint32_t num_coefs,
                              uint32_t point, uint32_t modulus) {
  point = point % modulus;
  uint32_t res = 0;
  for (int i=num_coefs-1; i>=0; i--) {
    res = ((uint64_t)(res) * point + coefs[i]) % modulus;
  }
  return res;
}



void _main() {

  // calldata is a concatenation of coef0 coef1 coef2 ... coefn point modulus
  uint32_t length = eth2_blockDataSize(); //length in bytes
  uint8_t* in = (uint8_t*) malloc( length * sizeof(uint8_t));
  eth2_blockDataCopy( (i32ptr*)in, 0, length ); //get calldata into memory
  int num_coefs = length/4-2;

  // something awkward about current ewasm: the bytes of each integer must be reversed
  // since ethereum data is big-endian and wasm memory is little-endian
  uint32_t* coefs = (uint32_t *) in;
  for (int i=0;i<num_coefs;i++){
    coefs[i] = reverse_bytes_32(coefs[i]);
  }
  uint32_t* point = (uint32_t *) (in+length-8);
  *point = reverse_bytes_32(*point);
  uint32_t* modulus = (uint32_t *) (in+length-4);
  *modulus = reverse_bytes_32(*modulus);

  // finally evaluate the polynomial
  uint32_t* out = (uint32_t*) malloc( 32);
  *out = PolynomialEvaluation(coefs, num_coefs, *point, *modulus);
  //*out = 0x36949fcc;
  *out = reverse_bytes_32(*out); // back to big-endian
  eth2_savePostStateRoot(out);

}

// test:
// coefs: 0x4f8d3b24 0x2799459c 0x47c1e7c2 0x3d2f68b8 0x0bef666e 0x4fb11ed6 0x33c4e081 0x0e47e61e 0x1c1b8f35 0x1ae2ca01
// point: 0x4dad39cf
// modulus: 0x57957121
// value of evaluated polynomial: 0x36949fcc
// test calldata and returndata: 0x4f8d3b242799459c47c1e7c23d2f68b80bef666e4fb11ed633c4e0810e47e61e1c1b8f351ae2ca014dad39cf57957121 0x36949fcc

