import time
import requests

BASE_URL = "http://127.0.0.1:8000"

ENDPOINTS = [
    "/companies/",
    "/companies/?sector=Tecnologia&sort_by=revenue&order=desc",
    "/companies/stats",
    "/cities/",
    "/cities/?state=SP&sort_by=population&order=desc",
    "/cities/stats",
]


def measure(url: str) -> tuple[float, str]:
    """Mede o tempo de resposta e retorna o status do cache."""
    start = time.perf_counter()
    resp = requests.get(url)
    elapsed = (time.perf_counter() - start) * 1000  # em ms
    cache_status = resp.headers.get("X-Cache", "N/A")
    return elapsed, cache_status


def main():
    # Limpa o cache antes de começar
    requests.delete(f"{BASE_URL}/cache/clear")
    print("Cache limpo!\n")
    print(f"{'Endpoint':<60} {'MISS (ms)':<12} {'HIT (ms)':<12} {'Speedup':<10}")
    print("-" * 94)

    for endpoint in ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"

        # Primeira requisição (MISS — vai ao banco)
        miss_time, _ = measure(url)

        # Segunda requisição (HIT — vem do cache)
        hit_time, _ = measure(url)

        speedup = miss_time / hit_time if hit_time > 0 else 0

        print(f"{endpoint:<60} {miss_time:<12.2f} {hit_time:<12.2f} {speedup:<10.1f}x")

    print("\nDone!")


if __name__ == "__main__":
    main()