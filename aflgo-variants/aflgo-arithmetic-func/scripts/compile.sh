rm ../distance_calculator/CMakeCache.txt
cd ..
make clean all
cd llvm_mode
make clean all
cd ..
cd distance_calculator/
cmake -G Ninja ./
cmake --build ./