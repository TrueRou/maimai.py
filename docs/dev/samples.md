# Sample Projects

For some of the complex features, we have provided interactive sample projects for developers to test and learn from.

Note that these projects are intended for advanced developers only, and you may not need to read this section if you just want to use the basic functionality of `maimai.py`.

Before running the sample projects, please follow the instructions below to configure the maimai.py development environment:

1. Download and enter the root directory of the project: `git clone https://github.com/TrueRou/maimai.py.git && cd maimai.py`
2. Create and activate the Poetry environment: `pip install poetry && poetry install && poetry shell`.
3. Enter the example directory: `cd examples && cd proxy_updater`
4. Run the example project: `python main.py

Now, the example project environment has been configured, and you can experience the following example projects

- **proxy_updater**: Sample program for `maimai.wechat()` and `WechatProvider()`

## proxy_updater

### Configuration

proxy_updater is an example of updating the prober using proxy and WeChat OAuth authentication, similar to the bakapiano / UsagiPass solution.

After running `python main.py` for the first time, `config.json` and `proxy.yaml` will be generated in the directory, which are the project's configuration file and proxy's configuration file.

You can modify the IP and port defined in `config.json` and `proxy.yaml` to suit your workspace environment.

> `proxy.yaml` is a configuration file for **Clash** that can be imported into any proxy tool that supports the Clash configuration

The configuration file allows you to enable or disable the uploading to each probers. For divingfish prober uploads, you need to provide your username and password, and for LXNS, you need to provide your friend code and developer token.

> For divingfish prober upload, you can use `Import-Token`, just leave the username empty and put `Import-Token` in the `credentials`.

After modifying the configuration file, restart the program, you can now test the sample project. 

### Using

After the program starts, it will prompt to click enter to generate a `Wechat URL`, after the user clicks enter, the program will generate a Wechat verification link.

Copy the link and open it in WeChat on the device with **Proxy** running to start the import process.

> Due to the WeChat verification system, the verification link expires quickly, once it expires you can see the error message in the CLI and simply regenerate it.

### Principle

The principle refers to [Bakapiano program](https://github.com/bakapiano/maimaidx-prober-proxy-updater), here quote Bakapiano's original words:

> Modify the redirect_uri link in WeChat OAuth2 authentication, change https://example.com to http://example.com and intercept it via HTTP proxy. After that, the server will get the Maimai score data through the authentication information. Theoretically, all platforms are supported, as long as the built-in WeChat browser on the corresponding platform uses the global HTTP proxy.

We provide `maimai.wechat()` method and `maimai.scores(wx_player, ScoreKind.ALL, WechatProvider())` method to wrap the above principle, which is convenient for developers to invoke.

The implementation can be found in the `updater.py` file in the sample project.