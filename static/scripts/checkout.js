const price = document.getElementById("price");
const qty = document.getElementById("qty");

const delivery = document.getElementById("del");
const dis_per = document.getElementById("dis-per")
const discount = document.getElementById("dis")

const total = document.getElementById("total");
const total_in = document.getElementById("total-in")

function pay() {
    let x = (parseFloat(price.innerHTML) * parseFloat(qty.value));

    x += parseFloat(delivery.innerHTML);

    let dis = (parseFloat(dis_per.innerHTML)/100 * x);

    x -= dis

    discount.innerHTML = dis.toFixed(2);
    total.innerHTML = x.toFixed(2);
    total_in.value = x;
}

pay()