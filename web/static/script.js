//some constant
const lengthOfVector = 50;

const stageWidth = document.getElementsByName('preview')[0].offsetWidth - 15;
const stageHeight = document.getElementsByName('controller')[0].offsetHeight;

// konva stage

var stage = new Konva.Stage({
    container: 'canvas1',
    width: stageWidth,
    height: stageHeight,
    offsetx: 0,
    offsety: 0,
});


// layer for image
var imgLayer = new Konva.Layer();
stage.add(imgLayer);
var img = new Image();

// get the new size i
function resizeImage(img) {
    let x = 0;
    let y = 0;
    let width = img.width;
    let height = img.height;
    if (height / width < stageWidth / stageHeight) {
        height = stageWidth / width * height;
        width = stageWidth;

    } else {
        width = stageHeight / height * width;
        height = stageHeight;
    }
    img = new Konva.Image({x: x, y: y, image: img, width: width, height: height});
    return img
}

function loadImage() {
    var file = document.getElementsByName('file')[0].files[0]
    var reader = new FileReader();
    if (file) {
        fileName = file.name
        reader.readAsDataURL(file)
    }
    ;
    reader.addEventListener("load", function () {
            img = new Image();
            img.src = reader.result;
            img.onload = function () {
                img = resizeImage(img);
                imgLayer.add(img);
                imgLayer.batchDraw();
            };
        },
        false
    );
}

// layer for pith
var pithLayer = new Konva.Layer();
var pithPoint = new Konva.Circle({
    x: -5,
    y: -5,
    radius: 5,
    fill: 'red',
    stroke: 'black',
    strokeWidth: 2,
    draggable: false,
});
var isDrawPith = false;

pithLayer.add(pithPoint);
stage.add(pithLayer);

// layer for pith
var angleLayer = new Konva.Layer();
var angleVector = new Konva.Arrow({
    points: [-10, -10, -10, -10],
    pointerLength: 3,
    pointerWidth: 3,
    fill: 'red',
    stroke: 'red',
    strokeWidth: 4,
    draggable: false,
});
angleLayer.add(angleVector)
stage.add(angleLayer);

var isDrawAngle = false;
var isDrawFirstAnglePoint = false;
var posStart = {x: NaN, y: NaN};
var posEnd = {x: NaN, y: NaN};

//actions for annotation
stage.on('mousedown touchstart', function (e) {
    if (isDrawPith) {
        var pos = stage.getPointerPosition();
        pithPoint.setAttr('x', pos.x)
        pithPoint.setAttr('y', pos.y)
        pithLayer.batchDraw();
        updateValues(Math.round(pos.x), 'pithx');
        updateValues(Math.round(pos.y), 'pithy');
        //isDrawPith = false;
    }
    if (isDrawAngle) {
        var pos = stage.getPointerPosition();
        posStart = {x: pos.x, y: pos.y};
        isDrawFirstAnglePoint = true;
    }
});

stage.on('mousemove touchmove', function (e) {
    if (isDrawAngle && (isDrawFirstAnglePoint)) {
        var pos = stage.getPointerPosition();
        if (Math.abs(posStart.x - pos.x) > 5 || Math.abs(posStart.y - pos.y) > 5) {
            angleVector.setAttr('points', [posStart.x, posStart.y, pos.x, pos.y])
            angleLayer.batchDraw();
            posEnd = {x: pos.x, y: pos.y};
            var degree = getDegreeOfVector(posStart.x, posStart.y, pos.x, pos.y);
            updateValues(degree, 'mark_angle');
        }
    }

})

stage.on('mouseup touchend', function (e) {
    if (isDrawAngle) {
        isDrawFirstAnglePoint = false;
        //posStart = {x: 0, y: 0};
    }
})

function updateDisabled() {
    document.getElementsByName("pithx")[0].readOnly = !isDrawPith;
    document.getElementsByName("pithy")[0].readOnly = !isDrawPith;
    document.getElementsByName("mark_angle")[0].readOnly = !isDrawAngle;
    if (isDrawPith) {
        document.getElementsByName("pith_reset")[0].classList.remove('disabled')
    } else {
        document.getElementsByName("pith_reset")[0].classList.add('disabled')
    }
    if (isDrawAngle) {
        document.getElementsByName("angle_reset")[0].classList.remove('disabled')
    } else {
        document.getElementsByName("angle_reset")[0].classList.add('disabled')
    }
}

function selectFromImage(e) {
    var name = e.name;
    var checked = e.checked;

    switch (name) {
        case "pith_from_image":
            isDrawPith = checked;
            if (checked) {
                isDrawAngle = false;
                document.getElementsByName("angle_from_image")[0].checked = false;
            }
            break;
        case "angle_from_image":
            isDrawAngle = checked;
            if (checked) {
                isDrawPith = false;
                document.getElementsByName("pith_from_image")[0].checked = false;
            }
            break;
    }
    updateDisabled();
}

function resetSelect(e) {
    var name = e.name;
    if (name == "pith_reset") {
        pithPoint.setAttr('x', -10);
        pithPoint.setAttr('y', -10);
        pithLayer.batchDraw();
        document.getElementsByName('pithx')[0].value = null;
        document.getElementsByName('pithy')[0].value = null;
    } else {
        angleVector.setAttr('points', [-10, -10, -10, -10]);
        angleLayer.batchDraw();
        document.getElementsByName('mark_angle')[0].value = null;
    }
}

function updateValues(value, name) {
    document.getElementsByName(name)[0].value = value;
}

// compute the degree of vector [0,360)
function getDegreeOfVector(x0, y0, x1, y1) {
    var x = x1 - x0;
    var y = y1 - y0;
    return Math.round(-1 * Math.sign(y) * Math.acos(x / Math.sqrt(x * x + y * y)) * 180 / Math.PI + 360) % 360;
}

function deg2rad(degree) {
    var rad = Math.PI * degree / 180;
    return rad
}

// update points and vectors by direct input
function updatePoint(e) {
    var name = e.name;
    if (name.search("pith") >= 0) {
        var x = parseInt(document.getElementsByName('pithx')[0].value);
        var y = parseInt(document.getElementsByName('pithy')[0].value);
        if (!isNaN(x) && !isNaN(y)) {
            pithPoint.setAttr('x', x)
            pithPoint.setAttr('y', y)
            pithLayer.batchDraw();
        }
    } else {
        var x0 = parseInt(document.getElementsByName('pithx')[0].value);
        var y0 = parseInt(document.getElementsByName('pithy')[0].value);
        var degree = parseInt(document.getElementsByName('mark_angle')[0].value);
        x0 = isNaN(x0) ? posStart.x : x0;
        y0 = isNaN(y0) ? posStart.y : y0;
        x0 = isNaN(x0) ? stage.width() / 2 : x0;
        y0 = isNaN(y0) ? stage.height() / 2 : y0;
        if (!isNaN(degree)) {
            x1 = x0 + Math.round(Math.sin(deg2rad(degree) + Math.PI / 2) * lengthOfVector);
            y1 = y0 + Math.round(Math.cos(deg2rad(degree) + Math.PI / 2) * lengthOfVector);
            angleVector.setAttr('points', [x0, y0, x1, y1]);
            angleLayer.batchDraw();
        }
    }
}

