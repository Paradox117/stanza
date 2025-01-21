const main = document.getElementById("main");

const table = {"A": "Z", "B": "A", "C": "B", "D": "C", "E": "D", "F": "E", "G": "F", "H": "G", "I": "H", "J": "I", "K": "J", "L": "K", "M": "L", "N": "M", "O": "N", "P": "O", "Q": "P", "R": "Q", "S": "R", "T": "S", "U": "T", "V": "U", "W": "V", "X": "W", "Y": "X", "Z": "Y", " ": " ", "'": "'", "!": "!", "?": "?", ".": ".", ",": ","}

const sleep = (ms) =>
  new Promise(resolve => setTimeout(resolve, ms));

const dcode = async() => {
    for (let i = 0; i < main.innerText.length; i++) {
        let char = main.innerText[i]
        if (char in [" ", "!", "'", ".", ",", "?"]) {

        } else {
            for (let j = 0; j < 5; j++) {
                if (char == char.toUpperCase()){
                    char = table[char.toUpperCase()].toUpperCase()
                } else {
                    char = table[char.toUpperCase()].toLowerCase()
                }
                
                shift(char, i)
                await sleep(30);
            }
        }
    }
}

function shift (char, i) {
    main.innerText = main.innerText.slice(0, i) + char + main.innerText.slice(i+1)
}

