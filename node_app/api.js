const express = require("express");
const app = express();
const bodyParser = require("body-parser");
const compiler = require("compilex");
const cors = require("cors");
const getPort = require('get-port');

const options = { stats: true };
compiler.init(options);

app.use(cors()); // Enable CORS for all origins

app.use(bodyParser.json());

// Serve the codemirror library statically
app.use("/codemirror-5.65.16", express.static("G:\edu_bot_compiler\codemirror\codemirror-5.65.16"));

// Serve the index.html file
app.get("/", function (req, res) {
    res.sendFile("G:/edu_bot_compiler/index.html");
});

// CORS preflight handling for /compile route
app.options("/compile", cors()); // Enable OPTIONS for /compile route

// Compilation endpoint
app.post("/compile", function (req, res) {
    const code = req.body.code;
    const input = req.body.input;
    const lang = req.body.lang;

    try {
        if (lang === "cpp") {
            const envData = { OS: "windows", cmd: "g++", options: { timeout: 10000 } };

            if (!input) {
                compiler.compileCPP(envData, code, function (data) {
                    if (data.output) {
                        res.send(data);
                    } else {
                        res.send({ output: "error" });
                    }
                });
            } else {
                compiler.compileCPPWithInput(envData, code, input, function (data) {
                    if (data.output) {
                        res.send(data);
                    } else {
                        res.send({ output: "error" });
                    }
                });
            }
        } else if (lang === "java") {
            const envData = { OS: "windows", options: { timeout: 10000 } };

            if (!input) {
                compiler.compileJava(envData, code, function (data) {
                    if (data.output) {
                        res.send(data);
                    } else {
                        res.send({ output: "error" });
                    }
                });
            } else {
                compiler.compileJavaWithInput(envData, code, input, function (data) {
                    if (data.output) {
                        res.send(data);
                    } else {
                        res.send({ output: "error" });
                    }
                });
            }
        } else if (lang === "python") {
            const envData = { OS: "windows", options: { timeout: 10000 } };

            if (!input) {
                compiler.compilePython(envData, code, function (data) {
                    if (data.output) {
                        res.send(data);
                    } else {
                        res.send({ output: "error" });
                    }
                });
            } else {
                compiler.compilePythonWithInput(envData, code, input, function (data) {
                    if (data.output) {
                        res.send(data);
                    } else {
                        res.send({ output: "error" });
                    }
                });
            }
        } else {
            res.status(400).send({ output: "Unsupported language" });
        }
    } catch (error) {
        res.status(500).send({ output: "Server error" });
    }
});

// Handle missing routes
app.use((req, res) => {
    res.status(404).send({ output: "Not Found" });
});

getPort().then(port => {
    app.listen(port, function () {
        console.log(`Server is running on port ${port}`);
    });
});
