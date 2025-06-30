# How to Cross-Compile Applications for Kakip

## 1. Introduction

This document provides an instruction for developers on how to set up a cross-compilation environment on a x86_64 Ubuntu host to build applications for the Kakip (ARM64) platform.

**What is Cross-Compilation?**

Cross-compilation is the process of creating an executable file on one platform (the "host," e.g., a x86_64 PC) that is intended to run on a different platform (the "target," e.g., an ARM64 embedded device). This is a standard practice in embedded development, as the host machine is typically much more powerful and has a better development environment than the target device.

This tutorial covers:

*   The "lazy way" of compiling natively on the target device.
*   Installing the ARM64 cross-compilation toolchain on the host.
*   Cross-compiling using a traditional Makefile.
*   Cross-compiling using CMake for a modern, scalable approach.

## 2. Prerequisites

*   **Host Machine**: A x86_64 computer running Ubuntu 24.04 LTS or a newer version.
*   **Target Device**: An Kakip running Ubuntu 24.04 LTS.
*   **Permissions**: You will need `sudo` privileges to install packages on both machines.

## 3. An Alternative: The "Lazy Way" (Native Compilation)

Before diving into cross-compilation, let's cover a more straightforward alternative: compiling directly on your ARM64 target device.

#### Advantages
*   **Simplicity**: There's no need to install a cross-compiler or configure complex toolchain files.
*   **Perfect Environment Matching**: You build in the exact same environment where the code will run, eliminating potential library version mismatches.

#### Disadvantages
*   **Slow Compilation Speed**: The processing power and memory of an Kakip is typically far inferior to a x86 development host. For large projects, compilation can be extremely time-consuming.
*   **Resource Constraints**: The target device may lack sufficient RAM or storage to build large-scale applications.

### How to Do It

#### Step 3.1: Prepare the Sample Code

On your **x86 host machine**, create a file named `main.cpp`. We use a preprocessor directive to show which binary is running.

```cpp
#include <iostream>

int main() {
    std::cout << "Hello Kakip!" << std::endl;

    return 0;
}
```

#### Step 3.2: Transfer the Source Code to the Kakip

```bash
# Run this on your x86 host machine
# (Replace with your target's user and IP address)
scp main.cpp ubuntu@<target-ip-address>:~/
```

#### Step 3.3: Install Build Tools on the Kakip

Login to your Kakip and install the `build-essential` package, which includes `gcc`, `g++`, `make`, and other common utilities.

```bash
# --- Run this on your ARM64 target device ---
sudo apt update
sudo apt install build-essential
```

#### Step 3.4: Compile Natively and Run on the Kakip

```bash
# --- Run this on your ARM64 target device ---
# Compile the code, defining the NATIVE_BUILD macro
g++ main.cpp -o hello_native

# Make it executable and run it
chmod +x hello_native
./hello_native
```
You will see the output message indicating a native build.

In short, by copying your source code to Kakip and installing the corresponding development packages, you’ll be able to compile and install it directly on the target platform.

---

## 4. Cross-Compilation: The Recommended Method

For any serious or large-scale project, cross-compilation is the more efficient and professional choice.

### Step 4.1: Install the Cross-Compilation Toolchain on the Host

On your **x86 Ubuntu host**, install the GCC toolchain for ARM64 platform.

```bash
# --- Run this on your x86 host machine ---
sudo apt update
sudo apt install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
```
Verify the installation was successful:
```bash
aarch64-linux-gnu-gcc -v
```

### Step 4.2: Prepare the Sample Code
We will use the same `main.cpp` file created in Step 3.1.

Then adopts the same command to manual compile the cpp file using ARM64 based compiler
```bash
aarch64-linux-gnu-g++ main.cpp -o hello_native
```

## 5. Example 1: Cross-Compiling with a Makefile

A Makefile is a classic and powerful build tool.

#### Create the Makefile

On your **x86 host**, in the same directory as `main.cpp`, create a file named `Makefile`:

```makefile
# Cross-compiler configuration
CXX = aarch64-linux-gnu-g++

# Compiler flags (-static makes the binary more portable)
CXXFLAGS = -Wall -O2 -static

# Target executable name
TARGET = hello_arm64_makefile

all: $(TARGET)

$(TARGET): main.cpp
	$(CXX) $(CXXFLAGS) -o $(TARGET) main.cpp
	@echo "Build complete! Target: $(TARGET)"

clean:
	rm -f $(TARGET)
```

#### Compile and Verify

```bash
# --- Run this on your x86 host machine ---
make
```
Use the `file` command to confirm the architecture of the resulting binary:
```bash
file hello_arm64_makefile
```
The output should clearly identify the file as `ARM aarch64`:
```
hello_arm64_makefile: ELF 64-bit LSB executable, ARM aarch64, version 1 (SYSV), ...
```
> **Note:** This is just an example.  
> If you already have an existing project with source code and a Makefile,  
> please make sure to update the compiler settings accordingly:

- For **C Language based** projects, set the compiler flag:
  ```make
  CC=aarch64-linux-gnu-gcc
  ```

- For **C++ based** projects, set the compiler flag:
  ```make
  CXX=aarch64-linux-gnu-g++
  ```

## 6. Example 2: Cross-Compiling with CMake

CMake is the preferred choice for modern projects, using a "Toolchain File" to manage cross-compilation.

#### Step 6.1: Create the CMake Toolchain File

On your **x86 host**, create a file named `aarch64.toolchain.cmake`:

```cmake
# Set the target system
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

# Specify the cross-compilers
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

```

#### Step 6.2: Create the CMakeLists.txt

In the same directory, create `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.16)
project(CrossCompileExample CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# For easy deployment, link statically
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static")

add_executable(hello_arm64_cmake main.cpp)

message(STATUS "Building for system: ${CMAKE_SYSTEM_NAME} ${CMAKE_SYSTEM_PROCESSOR}")
```

#### Step 6.3: Compile and Verify

Use an "out-of-source" build process:

```bash
# --- Run this on your x86 host machine ---
# 1. Create a build directory and enter it
mkdir build
cd build

# 2. Run cmake, specifying the toolchain file
cmake .. -DCMAKE_TOOLCHAIN_FILE=../aarch64.toolchain.cmake

# 3. Build the project
cmake --build .
or
make
```
Verify the resulting binary in `build/hello_arm64_cmake`:
```bash
file hello_arm64_cmake
```
The output will again show that it is an `ARM64` executable for Kakip.

## 7. Running the Cross-Compiled Binaries on the Target

Transfer the cross-compiled executables to your Kakip board and run them.

```bash
# --- Run this on your x86 host machine ---
# (Replace with your target's user and IP address)
scp hello_arm64_makefile ubuntu@<target-ip-address>:~/
scp build/hello_arm64_cmake ubuntu@<target-ip-address>:~/

# --- Run this on your ARM64 target device ---
chmod +x hello_arm64_makefile
./hello_arm64_makefile

chmod +x hello_arm64_cmake
./hello_arm64_cmake
```
You will see the output message indicating a cross-compiled build.

This is just a simple example.

If your CMake project is more complex, the first thing you should do is replace the toolchain with one targeted for Kakip. In some cases, you may also need to replace the sysroot. When that happens, you'll need to specify the appropriate path manually.

For large projects, it's often recommended to use a "lazy" approach—such as setting up an ARM64 environment using QEMU,so you can compile within the target environment directly, and avoid having to make excessive changes to the original source code.




## 8. Summary

| Method | Advantages | Disadvantages | Best For |
| :--- | :--- | :--- | :--- |
| **Native Compilation** | Simple, no dependency issues | Slow, limited by device resources | Quick tests, tiny projects |
| **Cross-Compile (Makefile)** | Fast, uses host power | Manual setup, less scalable | Small to medium projects |
| **Cross-Compile (CMake)** | Fast, professional, very scalable | Slightly more initial setup | Medium to large projects |


## 9. Example

Example 1. [kakip_ai_apps/R01_object_detection](https://github.com/YDS-Kakip-Team/kakip_ai_apps/tree/main/R01_object_detection)

Please follow this patch to modify the source code for the cross-compile environment

```bash
diff --git a/R01_object_detection/src/CMakeLists.txt b/R01_object_detection/src/CMakeLists.txt
index fdf4306..63b260f 100755
--- a/R01_object_detection/src/CMakeLists.txt
+++ b/R01_object_detection/src/CMakeLists.txt
@@ -8,11 +8,14 @@ include_directories(${TVM_ROOT}/include)
 include_directories(${TVM_ROOT}/3rdparty/dlpack/include)
 include_directories(${TVM_ROOT}/3rdparty/dmlc-core/include)
 include_directories(${TVM_ROOT}/3rdparty/compiler-rt)
+include_directories(SYSTEM ${CMAKE_SYSROOT}/usr/include/renesas/opencv4)
+include_directories(SYSTEM ${CMAKE_SYSROOT}/usr/include/renesas/)

-set(OpenCVA_INCLUDE_DIRS /usr/include/renesas/opencv4)
+
+set(OpenCVA_INCLUDE_DIRS ${CMAKE_SYSROOT}/usr/include/renesas/opencv4)
 set(OpenCVA_LIBS opencv_imgcodecs opencv_imgproc opencv_core opencv_highgui opencv_videoio)

-set(TVM_RUNTIME_LIB /usr/lib/aarch64-linux-gnu/renesas/libtvm_runtime.so)
+set(TVM_RUNTIME_LIB ${CMAKE_SYSROOT}/usr/lib/aarch64-linux-gnu/renesas/libtvm_runtime.so)
 set(EXE_NAME object_detection)

 file(GLOB SOURCE *.cpp *.h)
@@ -20,14 +23,14 @@ add_executable (${EXE_NAME}
 ${SOURCE}
 )

-target_link_directories(${EXE_NAME} PUBLIC /usr/lib/aarch64-linux-gnu/renesas)
+target_link_directories(${EXE_NAME} PUBLIC ${CMAKE_SYSROOT}/usr/lib/aarch64-linux-gnu/renesas)

 target_link_libraries(${EXE_NAME} pthread)
 target_link_libraries(${EXE_NAME} jpeg)
 target_link_libraries(${EXE_NAME} mmngr mmngrbuf)
 target_link_libraries(${EXE_NAME} ${OpenCVA_LIBS})

-target_include_directories(${EXE_NAME} PUBLIC /usr/include/renesas ${OpenCVA_INCLUDE_DIRS})
+target_include_directories(${EXE_NAME} PUBLIC ${CMAKE_SYSROOT}/usr/include/renesas ${OpenCVA_INCLUDE_DIRS})
 target_link_libraries(${EXE_NAME} ${TVM_RUNTIME_LIB})

 target_compile_definitions(${EXE_NAME} PRIVATE V2H)
```

```bash
vim R01_object_detection/src/aarch64.toolchain.cmake
# Set the target system
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

# Specify the cross-compilers
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

# Specify the sysroot path (example)
set(CMAKE_SYSROOT /home/wig/workspace/kakip/mnt)

# Add the --sysroot flag to the compiler and linker flags.
# This tells the compiler to look for headers and libraries in the specified sysroot.
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} --sysroot=${CMAKE_SYSROOT}" CACHE STRING "C compiler flags")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --sysroot=${CMAKE_SYSROOT}" CACHE STRING "CXX compiler flags")
# For the linker as well
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} --sysroot=${CMAKE_SYSROOT}")
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} --sysroot=${CMAKE_SYSROOT}")
set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} --sysroot=${CMAKE_SYSROOT}")

# Configure how CMake finds things. This is redundant if --sysroot works, but good practice.
set(CMAKE_FIND_ROOT_PATH ${CMAKE_SYSROOT})
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
```

Note that because R01_object_detection case need a **sysroot** rootfs, you can just mount the Kakip Ubuntu's uSD card on the host PC, then set the CMAKE_SYSROOT property to the cmake environment, then it will works.

Compile commands:

```bash
$ cd R01_object_detection/src/
$ mkdir build
$ cd build
$ cmake .. -DCMAKE_TOOLCHAIN_FILE=aarch64.toolchain.cmake
$ make

# Then copy the execute file to the Kakip board
$ scp -rv object_detection ubuntu@<target-ip-address>:~/
```

Please note that CMake projects often vary depending on the library dependencies. This is just a starting point to help everyone understand the process.
