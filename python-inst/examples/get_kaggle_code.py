import os, kaggle

for i in range(1, 2) :
    kernel_list = kaggle.api.kernels_list(page = i, page_size = 5)

    for kernel in kernel_list :
        print(kernel.ref)
        kaggle.api.kernels_pull(kernel.ref, os.path.join(os.getcwd(), kernel.ref), metadata=True)