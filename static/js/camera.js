const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const preview = document.getElementById("preview");

const captureBtn = document.getElementById("capture");
const retakeBtn = document.getElementById("retake");
const uploadBtn = document.getElementById("upload");

let imageBlob = null;

async function startCamera() {

    console.log("Secure Context:", window.isSecureContext);
    console.log("navigator:", navigator);
    console.log("mediaDevices:", navigator.mediaDevices);

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {

        alert(
            "Camera API not available.\n\n" +
            "Secure Context: " + window.isSecureContext +
            "\nmediaDevices: " + navigator.mediaDevices
        );

        return;
    }

    try {

        const stream = await navigator.mediaDevices.getUserMedia({

            video: {
                facingMode: "environment"
            },

            audio: false

        });

        video.srcObject = stream;

    }
    catch (err) {

        console.error(err);

        alert(err.name + "\n" + err.message);

    }

}

startCamera();

captureBtn.onclick = function(){

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    canvas.toBlob(function(blob){

        imageBlob = blob;

        preview.src = URL.createObjectURL(blob);

        preview.style.display="block";

        video.style.display="none";

        captureBtn.style.display="none";

        retakeBtn.style.display="inline-block";

        uploadBtn.style.display="inline-block";

    },"image/jpeg",0.95);

};

retakeBtn.onclick=function(){

    preview.style.display="none";

    video.style.display="block";

    captureBtn.style.display="inline-block";

    retakeBtn.style.display="none";

    uploadBtn.style.display="none";

};

uploadBtn.onclick=function(){

    const formData = new FormData();

    formData.append(
        "document",
        imageBlob,
        "scan.jpg"
    );

    fetch("/upload-camera",{

        method:"POST",

        body:formData

    })

    .then(r=>r.json())

    .then(data=>{

        alert(data.message);

        location.reload();

    });

};