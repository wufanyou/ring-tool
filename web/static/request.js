var responseResult

// range function
var range = (start, end) => [...Array(end - start + 1)].map((_, i) => start + i);

// layout for graph
var layout = {
    autosize: true,
    width: 460,
    height: 500,
    margin: {
        l: 0,
        r: 0,
        b: 0,
        t: 0,
    },
    //paper_bgcolor: '#7f7f7f',
    //plot_bgcolor: '#c7c7c7'
};

// plot function
function plot(data) {
    let array = [
        {
            x: range(0, data['array'].length - 1),
            y: data['array'],
            type: 'scatter',
            mode: "line",
            line: {
                color: 'rgb(38, 166, 154)',
                width: 1.5
            }
        }
    ];
    var layout = {
        //title: 'output',
        font: {size: 12},
        height: 284,
    };
    var config = {
        //displaylogo: false,
        responsive: true,
    }
    Plotly.newPlot('canvas2', array, layout, config);
}

//request function
function send(action, formName) {
    document.getElementsByName('progress')[0].style.visibility = 'visible';
    var form = new FormData(document.getElementsByName(formName)[0]);
    form.append('canvas_height', stageHeight);
    form.append('canvas_width', stageWidth);
    fetch(action, {
        method: 'post',
        body: form
    })
        .then(response => response.json())
        .then(function (data) {
            responseResult = data;
            plot(data);
            document.getElementsByName('progress')[0].style.visibility = 'hidden'
        })
}

function fineTune(action, formName) {
    //document.getElementsByName('progress')[0].style.visibility = 'visible';
    if ('md5' in responseResult) {
        const form = new FormData(document.getElementsByName(formName)[0]);
        form.append('md5',responseResult.md5)
        fetch(action, {
            method: 'post',
            body: form
        })
            .then(response => response.json())
            .then(function (data) {
                responseResult = data;
                plot(data);
                //document.getElementsByName('progress')[0].style.visibility = 'hidden'
            })
    }

}