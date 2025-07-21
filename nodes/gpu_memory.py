import torch
import comfy.model_management
import gc
import time
import psutil

try:
    import cuda_malloc
except ImportError:
    print("Could not import cuda_malloc.")
    cuda_malloc = None

class RaketeGpuGarbageCollector:
    def __init__(self):
        pass

    @classmethod

    def INPUT_TYPES(s):
        return {
            "required": {
                "samples": ("LATENT",),
                "clear_cache": ("BOOLEAN", {
                    "default":True
                }),
                "clear_models": ("BOOLEAN", {
                    "default": True
                }),
            }
        }
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "garbage_collector"
    CATEGORY = "rakete"

    def get_memory_info(self, beforeOrAfter):
        process = psutil.Process()
        cpu_memory = process.memory_info().rss / 1024 / 1024

        logs = []
        gpu_allocated = 0
        gpu_reserved = 0
        if torch.cuda.is_available():
            gpu_allocated = torch.cuda.memory_allocated() / 1024 / 1024
            gpu_reserved = torch.cuda.memory_reserved() / 1024 / 1024
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024

            logs.append(f"\n[Memory Stats {beforeOrAfter}]:")
            logs.append(f"- CPU: {cpu_memory:.2f}MB")
            logs.append(f"- GPU:")
            logs.append(f"  allocated: {gpu_allocated:.2f}MB")
            logs.append(f"  reserved: {gpu_reserved:.2f}MB")
            logs.append(f"  total: {total_memory:.2f}MB")

        return cpu_memory, gpu_allocated, gpu_reserved, logs

    def garbage_collector(self, samples, clear_cache, clear_models):

        cpu_before, gpu_allocated_before, gpu_reserved_before, logs = self.get_memory_info("Before")

        s = samples.copy()

        if cuda_malloc is not None:
            if hasattr(cuda_malloc, 'get_cached_memory'):
                cached = cuda_malloc.get_cached_memory()
                if cached > 0:
                    cuda_malloc.free_cached_memory()

                if hasattr(cuda_malloc, 'get_memory_info'):
                    total, free, used = cuda_malloc.get_memory_info()
                    if used > 0:
                        logs.append(f"- cuda_malloc: {used/1024/1024:.2f}MB")

        if clear_models:
            if hasattr(comfy.model_management, 'unload_all_models'):
                comfy.model_management.unload_all_models()

                for obj in gc.get_objects():
                    try:
                        if torch.is_tensor(obj):
                            obj.storage().resize_(0)
                            del obj
                        elif hasattr(obj, 'data') and torch.is_tensor(obj.data):
                            obj.data.storage().resize_(0)
                            del obj.data
                    except:
                        pass

                if hasattr(comfy.model_management, 'current_loaded_models'):
                    comfy.model_management.current_loaded_models.clear()
                    comfy.model_management.models_need_reload = True

                if hasattr(comfy.model_management, 'vram_state'):
                    comfy.model_management.vram_state = None

                if hasattr(comfy.model_management, 'model_cache'):
                    comfy.model_management.model_cache.clear()

                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()

                time.sleep(0.5)

        if clear_cache:
            model_manager = comfy.model_management
            for cache_name in ['model_cache', 'vae_cache', 'clip_cache']:
                cache = getattr(model_manager, cache_name, None)
                if cache is not None and isinstance(cache, dict):
                    cache.clear()

            if hasattr(model_manager, 'soft_empty_cache'):
                model_manager.soft_empty_cache(force=True)

            gc.collect()

            if torch.cuda.is_available():
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats()
                torch.cuda.reset_max_memory_allocated()

            if hasattr(model_manager, 'models_need_reload'):
                model_manager.models_need_reload = True

        time.sleep(1)

        cpu_after, gpu_allocated_after, gpu_reserved_after, more_logs = self.get_memory_info("After")
        logs.extend(more_logs)

        cpu_freed = cpu_before - cpu_after
        gpu_allocated_freed = gpu_allocated_before - gpu_allocated_after
        gpu_reserved_freed = gpu_reserved_before - gpu_reserved_after

        logs.append(f"\n[Memory Release]:")
        logs.append(f"- CPU: {cpu_freed:.2f}MB")
        logs.append(f"- GPU allocated_freed: {gpu_allocated_freed:.2f}MB")
        logs.append(f"- GPU reserved_freed: {gpu_reserved_freed:.2f}MB")

        result_str = "\n".join(logs)
        print(result_str)

        return (s,)

NODE_CLASS_MAPPINGS = {
    "rakete.GpuGarbageCollector": RaketeGpuGarbageCollector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "rakete.GpuGarbageCollector": "GPU Garbage Collector",
}
