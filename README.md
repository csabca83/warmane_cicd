# Warmane daily point collector

Warmane daily point collector is a Python app for collecting the available daily points on the warmane website.

## How it works

It is using [heroku](https://dashboard.heroku.com/) as the main platform where multiple servers are being deployed for this purpose. The deployment is being handled through a CICD pipeline on heroku.
![Alt Text](https://res.cloudinary.com/practicaldev/image/fetch/s--gTKCW0D_--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_66%2Cw_880/https://thepracticaldev.s3.amazonaws.com/i/tzxcx9c1kowowai3mo3w.gif)

The deployment has a couple of tests through [travis ci](https://www.travis-ci.com/) before the pipeline triggers the build.
![Alt Text](https://user-images.githubusercontent.com/16547949/75810964-91ee2f80-5d59-11ea-8e50-2dd54b48d683.gif)

## Usage

```bash
#The following environment variables are optional on the heroku instance:
SCK          = AWS Secret Access key for browser caching s3
ACK          = AWS Access key for browser caching on s3

#The following environment variables are mandatory on the heroku instance
ACCESS_TOKEN = An access token for your facebook chatbot
mfa          = MFA for your website login
FB_ID        = An ID for the person who can interact and receive messages from the chatbot(owner presumably)
FIREFOX_BIN  = The binary location for firefox /app/.apt/usr/bin/firefox
warmane_acc  = Warmane account number
warmane_pass = Warmane password
wittoken     = An api token for wit.com
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Also be aware that the only accepted pull requests have to comply with the pep3 standards which are being done through flake8 precommit checks.
Also make sure to install pre-commit checks before you track your code changes.
```python
pip install pre-commit
```

![Alt Text](https://ljvmiranda921.github.io/assets/png/tuts/precommit_demo.gif)

## License
MIT License

Copyright (c) 2021 Csaba Seregy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.