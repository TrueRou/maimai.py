# Client

maimai.py provides a RESTful API client that you can call using any language via HTTP requests.

The client is compiled using Nuitka. Please download it from the [Releases](https://github.com/TrueRou/maimai.py/releases) page.

Our client supports Windows, MacOS, and Linux. Please download the appropriate version for your system.

## Usage

1. Download the appropriate client version.
2. Execute the client's binary file.
3. Wait for the client to initialize until you see `Uvicorn running on http://127.0.0.1:8000`.
4. Use any language to call maimai.py features via HTTP requests.

## Documentation

FastAPI provides auto-generated documentation. You can view the documentation and test features by visiting `http://127.0.0.1:8000/docs`.

Additionally, we provide an online preview of the API documentation, which you can view [here](https://openapi.maimai.turou.fun/).

## Example Codes

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
        // Example: Get song list
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
        // Example: Get song list
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

// Example: Get song list
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
    // Example: Get song list
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

## FastAPI Integration

If you are using FastAPI, you can integrate maimai.py into your FastAPI application.

```python
from fastapi import FastAPI
from maimai_py.api import router as maimai_router

app = FastAPI()
app.include_router(maimai_router, prefix="/maimai")
```

You can also run the built-in FastAPI server using the following command:

```bash
uvicorn maimai_py.api:app --port 1234 --host 0.0.0.0
```