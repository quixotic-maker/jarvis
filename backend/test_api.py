"""测试API端点并显示详细错误"""
import requests

def test_endpoint(url):
    print(f"\n测试: {url}")
    print("="*60)
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应: {response.json()}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"异常: {e}")

if __name__ == "__main__":
    base = "http://localhost:8000/api/v2"
    
    test_endpoint(f"{base}/schedules/")
    test_endpoint(f"{base}/tasks/")
    test_endpoint(f"{base}/settings/")
