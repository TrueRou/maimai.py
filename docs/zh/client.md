# 客户端

maimai.py 提供了 RESTful API 客户端, 您可以通过任何语言通过HTTP请求来调用 maimai.py 的特性。

客户端使用 Nuitka 编译，请在 [Releases](https://github.com/TrueRou/maimai.py/releases) 页面下载。

我们的客户端支持 Windows 和 Linux，请根据您的系统下载对应的版本。

## 使用方式

1. 下载对应的客户端版本
2. 执行客户端的二进制文件
3. 等待客户端初始化，直至出现 `Uvicorn running on http://127.0.0.1:8000` 字样
4. 使用任何语言通过HTTP请求来调用 maimai.py 的特性

## 关于文档

FastAPI 提供了自动生成的文档，您可以通过访问 `http://127.0.0.1:8000/docs` 来查看文档和测试功能。

另外，我们也提供了可以在线预览的API文档，您可以通过 [这里](https://openapi.maimai.turou.fun/) 查看。

## 调用示例

### Java

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpHeaders;

public class ApiClient {
    private static final String BASE_URL = "http://127.0.0.1:8000";

    public static void main(String[] args) {
        // 示例：获取歌曲列表
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/songs"))
                .header("Accept", "application/json")
                .build();

        try {
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            HttpHeaders headers = response.headers();
            System.out.println("Status Code: " + response.statusCode());
            headers.map().forEach((k, v) -> System.out.println(k + ":" + v));
            System.out.println("Response Body: " + response.body());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### C#

```csharp
using System;
using System.Net.Http;
using System.Threading.Tasks;

public class ApiClient
{
    private static readonly HttpClient client = new HttpClient();
    private static readonly string baseUrl = "http://127.0.0.1:8000";

    public static async Task Main(string[] args)
    {
        // 示例：获取歌曲列表
        client.DefaultRequestHeaders.Accept.Add(new System.Net.Http.Headers.MediaTypeWithQualityHeaderValue("application/json"));

        HttpResponseMessage response = await client.GetAsync(baseUrl + "/songs");
        response.EnsureSuccessStatusCode();

        string responseBody = await response.Content.ReadAsStringAsync();
        Console.WriteLine("Response Body: " + responseBody);
    }
}
```

### JavaScript
```javascript
const baseUrl = 'http://127.0.0.1:8000';

// 示例：获取歌曲列表
async function fetchSongs() {
    const response = await fetch(`${baseUrl}/songs`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json'
        }
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Response Body:', data);
}

fetchSongs().catch(error => {
    console.error('There was an error!', error);
});
```

### Go
```go
package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
)

const baseUrl = "http://127.0.0.1:8000"

func main() {
    // 示例：获取歌曲列表
    url := baseUrl + "/songs"
    req, err := http.NewRequest("GET", url, nil)
    if err != nil {
        fmt.Println("Error creating request:", err)
        return
    }

    req.Header.Set("Accept", "application/json")

    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        fmt.Println("Error sending request:", err)
        return
    }
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        fmt.Println("Error reading response body:", err)
        return
    }

    var data interface{}
    if err := json.Unmarshal(body, &data); err != nil {
        fmt.Println("Error unmarshalling response body:", err)
        return
    }

    fmt.Println("Response Body:", data)
}
```

## FastAPI集成

如果您希望在自己的 FastAPI 项目中集成 maimai.py，您可以通过以下方式来导入 maimai.py 的所有路由。

```python
from fastapi import FastAPI
from maimai_py.api import router as maimai_router

app = FastAPI()
app.include_router(maimai_router, prefix="/maimai")
```

您也可以使用 Uvicorn 来直接运行 maimai.py 内置的 FastAPI 服务。

```bash
uvicorn maimai_py.api:app --port 1234 --host 0.0.0.0
```