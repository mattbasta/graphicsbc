var c = $('canvas')[0];
$('button.run').on('click', function (e) {
    e.preventDefault();
    gbc.run(c, $('textarea').val());
});

$('button.compile').on('click', function (e) {
    e.preventDefault();
    console.log(gbc.compile(c, $('textarea').val()));
});
