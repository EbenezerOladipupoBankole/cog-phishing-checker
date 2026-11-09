# Inbox Guard

Not sure if an email is a scam? Inbox Guard takes a look. Give it one suspicious email, and it tells you how risky it looks, what gave it away, and the exact words that raised the flag.

I built it with [cog-smith](https://github.com/cogcloud-ai/cog-smith), to try out the [Cog Builder](https://github.com/cogcloud-ai/cog-op-builder) tools.

<img width="1897" height="914" alt="image" src="https://github.com/user-attachments/assets/51e2a097-2d06-4804-9589-2df505e188fa" />


## Example

A fake DHL email asking for a "customs fee" came back as **high risk**, with these warning signs:

| Warning sign | Words from the email |
|---|---|
| Urgency | "Your parcel will be returned to sender if the fee is not paid within 48 hours." |
| Asks for money | "Please pay now using the secure link below." |
| Fake sender | "notify@dhl-parcel-delivery.info" |
| Suspicious link | "http://dhl-fee-payment.xyz/pay" |

## How it stays honest

- Every warning quotes the email word for word, and the cog checks those quotes automatically.
- If there isn't enough to go on, it says "unsure" instead of guessing "safe."
- It never opens links, never sends anything, and ignores any instructions hidden in the email.

## Setup

You'll need Linux or macOS (on Windows, use WSL), [Pixi](https://pixi.sh) and [Ollama](https://ollama.com).

```bash
pixi install
pixi run test

ollama pull gemma3:12b
pixi run use -- --endpoint http://127.0.0.1:11434/v1 --model gemma3:12b \
    --locality local --response-format json_object --timeout 1800
```

## Use the web page

The easiest way to use it. Paste in an email and see the result, with the suspicious words highlighted. It runs on your own computer.

Open two terminals in the project folder:

```bash
# Terminal 1: start the cog
pixi run serve

# Terminal 2: start the page
python3 ui/serve_ui.py
```

Then open **http://127.0.0.1:8094** in your browser. When the dot at the top says **Ready**, paste in an email (or click **Load an example**) and click **Check email**. On a laptop without a graphics card, a check can take several minutes; the page shows a timer while it works.

## Use the terminal

```bash
pixi run ask -- --bundle examples/test-parcel.json
```

To check your own email, copy `examples/test-parcel.json` and swap in the details. Keep real emails out of Git.

## Where it's at

On a 16 GB laptop running Gemma 3 (CPU only), it correctly flagged two scam emails as high risk, including one it had never seen before. Each check took about 7 to 14 minutes.

It still needs work on safe emails: a genuine account notification was rated medium risk, because it mistook general safety advice ("update your passwords often") for a request for private details. That's the next thing to fix.

More details are in [COG.md](COG.md).
