#!/usr/bin/env python

import yaml
import shlex
import subprocess
import re
import durationpy


bench_yamls = [
              "blake2b_0.yaml", "blake2b_64.yaml", "blake2b_256.yaml", "blake2b_1024.yaml",
              "keccak256_0.yaml", "keccak256_64.yaml", "keccak256_256.yaml", "keccak256_1024.yaml",
              "sha256_0.yaml", "sha256_64.yaml", "sha256_256.yaml", "sha256_1024.yaml"
              ]


"""
$ ./benchmark-interp /wasmfiles/scout/wasm/sha256_rhash.wasm
parse succeeded..
execution finished...
register benchmark...
run benchmark...
2019-07-25 22:21:26
Running /Users/mbpro/wabt/out/clang/Release/benchmark-interp
Run on (12 X 2900 MHz CPU s)
CPU Caches:
  L1 Data 32K (x6)
  L1 Instruction 32K (x6)
  L2 Unified 262K (x6)
  L3 Unified 12582K (x1)
Load Average: 2.47, 2.28, 2.33
------------------------------------------------------
Benchmark            Time             CPU   Iterations
------------------------------------------------------
wabt_interp        734 us          732 us          859
"""

def do_wabt_bench(wabt_cmd):
    print("running wabt benchmark...\n{}\n".format(wabt_cmd))
    wabt_cmd = shlex.split(wabt_cmd)
    stdoutlines = []
    with subprocess.Popen(wabt_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout: # b'\n'-separated lines
            print(line, end='')
            stdoutlines.append(line)  # pass bytes as is
        p.wait()

    timeregex = "wabt_interp\s+(\d+) us"
    benchline = stdoutlines[-1]
    time_match = re.search(timeregex, benchline)
    us_time = durationpy.from_str("{}us".format(time_match.group(1)))
    return {'time': us_time.total_seconds()}




def run_yaml_file(yaml_filename, wabt_binary, engine_name):
    with open(yaml_filename, 'r') as stream:
        print("running yaml file:", yaml_filename)
        yaml_file = yaml.safe_load(stream)
        print(yaml_file['beacon_state']['execution_scripts'])
        wasm_files = yaml_file['beacon_state']['execution_scripts']
        input_data = yaml_file['shard_blocks'][0]['data']
        print('input_data:', input_data)
        with open('test_block_data.hex', 'w') as blockdata_file:
            blockdata_file.write(input_data)

        bench_results = []
        for bench_file in wasm_files:
            wasm_full_path = "/Users/mbpro/dev_ewasm/C_ewasm_contracts/scout/wasm/{}".format(bench_file)
            #wabt_command = "/Users/mbpro/dev_ewasm/wabt/out/clang/Release/wasm-interp {}".format(wasm_full_path)
            #wabt_command = "/Users/mbpro/dev_ewasm/wabt/out/clang/Release/benchmark-interp {}".format(wasm_full_path)
            wabt_command = "/Users/mbpro/dev_ewasm/wabt/out/clang/Release/{} {}".format(wabt_binary, wasm_full_path)
            wabt_result = do_wabt_bench(wabt_command)
            print("got time:", wabt_result)
            wabt_result['wasm_file'] = bench_file
            wabt_result['yaml_file'] = yaml_filename
            wabt_result['engine'] = engine_name
            bench_results.append(wabt_result)
            #print("running wabt benchmark...\n{}".format(wabt_command))
            #wabt_cmd = shlex.split(wabt_command)
            #with subprocess.Popen(wabt_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True) as p:
            #    for line in p.stdout: # b'\n'-separated lines
            #        print(line, end='')
            #    p.wait()

        return bench_results


all_bench_results = []
for scout_yaml in bench_yamls:
    yaml_file_results_baseline = run_yaml_file(scout_yaml, "benchmark-interp-baseline", "wabt-baseline")
    all_bench_results.extend(yaml_file_results_baseline)
    yaml_file_results_optimized = run_yaml_file(scout_yaml, "benchmark-interp-optimized", "wabt-optimized")
    all_bench_results.extend(yaml_file_results_optimized)

print("all bench results!")
print(all_bench_results)





