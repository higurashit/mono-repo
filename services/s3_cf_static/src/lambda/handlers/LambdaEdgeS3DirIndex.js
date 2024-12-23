exports.handler = (event, context, callback) => {
    var request = event.Records[0].cf.request;
    var olduri = request.uri;
    var newuri = olduri.replace(/\/$/, '\/index.html');

    console.log("Old URI: " + olduri);
    console.log("New URI: " + newuri);

    request.uri = newuri;
    return callback(null, request);
};
