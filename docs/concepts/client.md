# RESTful 客户端

如果您希望通过其他语言调用 maimai.py 的功能，或者希望在自己的项目中集成 maimai.py 的特性，我们提供了一个 RESTful API 客户端。

maimai.py 的 RESTful 客户端是基于 [FastAPI](https://fastapi.tiangolo.com/) 实现的，提供了一个简单易用的 HTTP 接口，您可以通过 HTTP 请求来调用 maimai.py 的功能。

## 使用 RESTful 客户端

通过将 FastAPI 程序打包为二进制文件，我们提供了一个独立的客户端，您可以在本地运行它，并通过 HTTP 请求来调用 maimai.py 的功能。

客户端使用 Nuitka 编译，请在 [Releases](https://github.com/TrueRou/maimai.py/releases) 页面下载。

我们的客户端支持 Windows 和 Linux，请根据您的系统下载对应的版本。执行 `maimai.py-platform-amd64 --help` 可以查看帮助信息。

![](https://imgur.com/nZGyDvf.png)

待客户端运行后，您可以通过 HTTP 请求来调用 maimai.py 的功能，您可以通过访问 `http://127.0.0.1:8000/docs` 来查看文档和测试功能。

另外，我们也提供了可以在线预览的API文档，您可以通过 [这里](https://openapi.maimai.turou.fun/) 查看。

## 集成 FastAPI 路由

如果您希望在自己的 FastAPI 项目中集成 maimai.py，您可以通过以下方式来创建 maimai.py 风格的路由。

```python
from fastapi import FastAPI
from maimai_py import MaimaiRoutes

app = FastAPI()
maimai_client = MaimaiClient()
routes = MaimaiRoutes(maimai_client, settings.lxns_developer_token, settings.divingfish_developer_token, settings.arcade_proxy)

app.include_router(routes.get_router(routes._dep_hybrid, skip_base=False), tags=["base"])
app.include_router(routes.get_router(routes._dep_lxns, routes._dep_lxns_player), prefix="/lxns", tags=["lxns"])
app.include_router(routes.get_router(routes._dep_divingfish, routes._dep_divingfish_player), prefix="/divingfish", tags=["divingfish"])
```

::: info
阅读 [simple_prober (示例项目)](../samples/simple_prober.md) 了解更多
:::

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

