const express = require("express");
const mysql = require("mysql2");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "",
    database: "webdemo"
});

db.connect((err) => {
    if (err) throw err;
    console.log("MySQL Connected");
});

app.get("/volunteers", (req, res) => {
    db.query("SELECT * FROM volunteers", (err, result) => {
        if (err) throw err;
        res.json(result);
    });
});

app.post("/volunteers", (req, res) => {
    const { name, city, experience } = req.body;

    db.query(
        "INSERT INTO volunteers (name, city, experience) VALUES (?, ?, ?)",
        [name, city, experience],
        (err, result) => {
            if (err) throw err;
            res.json({ id: result.insertId, name, city, experience });
        }
    );
});

app.listen(5000, () => {
    console.log("Server running on port 5000");
});