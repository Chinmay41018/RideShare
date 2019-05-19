var me = {};

var you = {};

var post_url = "https://qhgpzze3ij.execute-api.us-east-1.amazonaws.com/proj"

window.startv = "Whats your start location?";
window.end = "Whats the end location?";


function get_reply_message(text, json_string)
{
  console.log(typeof(text));
  console.log(text);
  console.log(text.data.body);
  // var rep = text.split("text")[1].split("timestamp")[0];
  // rep = rep.substring(4, rep.length-4);
  // console.log(rep);
  iter_ask_hacky_fix(text.data.body, json_string);
 
}

window.start_flag = 0;
window.end_flag = 0;

function get_reply_message_chat(text)
{
  var rep = text.split("text")[1].split("timestamp")[0];
  rep = rep.substring(4, rep.length-4);
  console.log(rep);
  insertChat("you",rep);
  if(rep==window.startv)
  {
    window.start_flag=1;
  }
  if(rep==window.end)
  {
    window.end_flag=1;
  }
  
}
// function get_reply_message_chat(text)
// {
//   console.log(typeof(text));
//   console.log(text);
//   console.log(text.data.body);
//   insertChat("you",text.data.body);

// }


function getTokenID()
{
    var href = window.location.href;
    var parts = href.split('#')[1].split('&');
    var id_token = parts[0].split('=')[1];
    var access_id = parts[1].split('=')[1];
    var expires_in = parts[2].split('=')[1];
    var token_type = parts[3].split('=')[1];
    return [id_token,access_id]

}
AWS.config.region = 'us-east-1';
var identityId = null;
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:04abd8d3-a6fd-4638-b100-7f9274d40074',
    Logins: {
      'cognito-idp.us-east-1.amazonaws.com/us-east-1_AjDnWanrT': getTokenID()[0]
    }
  });
  // var params = {
  //       IdentityPoolId: 'us-east-1:245ff226-43d4-4def-94d6-59adc6568f7e',
  //       Logins :{
  //           "cognito-idp.us-east-1.amazonaws.com/us-east-1_QWKk0Nsje" : getTokenID()
  //          }
  //     };
AWS.config.credentials.refresh((error) => {
    if (error) {
      console.error(error);
      console.log("Unauthorized");
      //  window.location.replace("https://cc2019.auth.us-east-1.amazoncognito.com/login?response_type=token&client_id=7uc2oojk9qnh5nue061pmf2up8&redirect_uri=https://d2zqo6rgcu4uz9.cloudfront.net");
  
    } else {
      console.log('Successfully logged!');
    }
  });


function iter_ask_hacky_fix(resp,json_string)
{
  if(resp=="false")
  {
    // url = alert("Please enter valid image url! We need to know you are a human.");
    var url = prompt("Please enter your url of your photograph (your url doesn't comply with our requirements):", "");
    var inp = {'body':url , 'user':json_string};
    call_check_photo(inp, json_string);
  }

  else
  {
  var op = prompt("Successfully logged in :) Congrats! If you want to drive, click 1 or else if you want a ride click 2:", "");
  console.log(op);
  console.log(typeof(op));
  if(op=="1")
  {
    driver();
    document.getElementById("lol").innerHTML = "Welcome, you are here to find riders!"
  }
  else if (op=="2")
  {
    rider();
    document.getElementById("lol").innerHTML = "Welcome, you are here to find a ride!"
  }
  else
    {alert("Dumass!");}

}
}

function checkPhoto()
{
  var arr = getTokenID();
  var at = arr[1];
  var payload = at.split('.')[1]
  var json_string = atob(payload);
  url = "";
  respnse = "false";
  inp = {'body':url , 'user':json_string}
  call_check_photo(inp, json_string)

  // if (response=="false")
  // {
  //   url = alert("Please enter valid image url! We need to know you are a human.")
  //   inp = {'url':url , 'user':json_string}
  //   call_check_photo(inp)





  // }



}


function call_check_photo(inp, json_string)
{
    var params = {
  // This is where any modeled request parameters should be added.
  // The key is the parameter name, as it is defined in the API in API Gateway.
    };

    var body = inp;

    var additionalParams = {
      // If there are any unmodeled query parameters or headers that must be
      // //   sent with the request, add them here.
      // headers: {
      // },
      // queryParams: {
      // }
    };
    // var reply='k';
    AWS.config.credentials.get(function() {
    
        apigClient = apigClientFactory.newClient({
          region: "us-east-1",
          accessKey: AWS.config.credentials.accessKeyId,
          secretKey: AWS.config.credentials.secretAccessKey,
          sessionToken: AWS.config.credentials.sessionToken
          
        });
 
        // console.log(AWS.config.credentials);
        
        apigClient.checkPost(params, body, additionalParams)
          .then(function (result) {
            // Add success callback code here.
            console.log(result);
            reply = result;
            // reply = result.data.body.messages[0].unstructured['text'];
            // return reply;
            // console.log(reply);
            // console.log("unable to go out why?");
            get_reply_message(reply, json_string);
            // return reply;
            

          }).catch(function (result) {
            reply = "Problem";
            // console.log("here2")
            // console.log(result)
            // return reply;
            // // Add error callback code here.
            // return reply;
          });

      });


    // return reply;

}

function formatAMPM(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
}            

//-- No use time. It is a javaScript effect.
function insertChat(who, text, time = 0){
    var control = "";
    var date = formatAMPM(new Date());
    
    if (who == "me"){
        
        control = '<li style="width:100%">' +
                        '<div class="msj macro">' +
                            '<div class="text text-l">' +
                                '<p>'+ text +'</p>' +
                                '<p><small>'+date+'</small></p>' +
                            '</div>' +
                        '</div>' +
                    '</li>';                    
    }else{
        control = '<li style="width:100%;">' +
                        '<div class="msj-rta macro">' +
                            '<div class="text text-r">' +
                                '<p>'+text+'</p>' +
                                '<p><small>'+date+'</small></p>' +
                            '</div>' +
                        '<div class="avatar" style="padding:0px 0px 0px 10px !important"></div>' +                                
                  '</li>';
    }
    setTimeout(
        function(){                        
            $("ul").append(control);

        }, time);
    
}

function resetChat(){
    console.log("Inside resetChat");
    $("ul").empty();
}
function enter_chat(e){
    if(e.keyCode=13){
    alert("The paragraph was clicked.");
  console.log("haha");}

}



function call_api_gateway_driver(inp)
{
    var params = {
  // This is where any modeled request parameters should be added.
  // The key is the parameter name, as it is defined in the API in API Gateway.
    };

  var arr = getTokenID();
  var at = arr[1];
  var payload = at.split('.')[1]
  var json_string = atob(payload);
    var body = {
      // This is where you define the body of the request,
      'body':inp,
      'userID':json_string
      // 'userID':getTokenID()[0],

    };
    console.log(body);

    var additionalParams = {
      // If there are any unmodeled query parameters or headers that must be
      // //   sent with the request, add them here.
      // headers: {
      // },
      // queryParams: {
      // }
    };
    // var reply='k';
    console.log("About to make a call...");
    AWS.config.credentials.get(function() {
    
        apigClient = apigClientFactory.newClient({
          region: "us-east-1",
          accessKey: AWS.config.credentials.accessKeyId,
          secretKey: AWS.config.credentials.secretAccessKey,
          sessionToken: AWS.config.credentials.sessionToken
          
        });
 
        // console.log(AWS.config.credentials);
        
        apigClient.driverPost(params, body, additionalParams)
          .then(function (result) {
            // Add success callback code here.
            console.log(result.data.body);
            reply = result.data.body;
            // reply = result.data.body.messages[0].unstructured['text'];
            // return reply;
            console.log(reply);
            console.log("unable to go out why?");
            get_reply_message_chat(reply);
            

          }).catch(function (result) {
            reply = "Problem";
            console.log("here2");
            console.log(result);
            // // Add error callback code here.
            // return reply;
          });

      });


    // return reply;

}



function call_api_gateway_rider(inp)
{
    var params = {
  // This is where any modeled request parameters should be added.
  // The key is the parameter name, as it is defined in the API in API Gateway.
    };
  var arr = getTokenID();
  var at = arr[1];
  var payload = at.split('.')[1]
  var json_string = atob(payload);
    var body = {
      // This is where you define the body of the request,
      'body':inp,
      'userID':json_string
      // 'userID':getTokenID()[0],

    };

    var additionalParams = {
      // If there are any unmodeled query parameters or headers that must be
      // //   sent with the request, add them here.
      // headers: {
      // },
      // queryParams: {
      // }
    };
    // var reply='k';
    AWS.config.credentials.get(function() {
    
        apigClient = apigClientFactory.newClient({
          region: "us-east-1",
          accessKey: AWS.config.credentials.accessKeyId,
          secretKey: AWS.config.credentials.secretAccessKey,
          sessionToken: AWS.config.credentials.sessionToken
          
        });
 
        // console.log(AWS.config.credentials);
        
        apigClient.riderPost(params, body, additionalParams)
          .then(function (result) {
            // Add success callback code here.
            console.log(result.data.body);
            reply = result.data.body;
            // reply = result.data.body.messages[0].unstructured['text'];
            // return reply;
            console.log(reply);
            console.log("unable to go out why?");
            get_reply_message_chat(reply);
            

          }).catch(function (result) {
            // reply = "Problem";
            // console.log("here2")
            // // Add error callback code here.
            // return reply;
          });

      });


    // return reply;

}



function driver(){

console.log("haha");
resetChat();
var input = document.getElementById("input");
console.log(input);
input.addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
   var text = $(this).val();
        if (text !== ""){
            insertChat("me", text);              
            $(this).val('');

            if (window.start_flag==1)
            {
                document.getElementById("from").value = text;
                document.getElementById("f").click(); 
                window.start_flag=0;
                // alert("Hi");
            }
            if (window.end_flag==1)
            {
                document.getElementById("to").value = text;
                document.getElementById("t").click(); 
                window.end_flag=0;
                document.getElementById("go").click();
                // alert("Hi");
            }

        }
    // var a =
    call_api_gateway_driver(text);
    // insertChat("you", reply);


  }
});
}

function rider(){
resetChat();
console.log("haha")

var input = document.getElementById("input");
input.addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {

   var text = $(this).val();
        if (text !== ""){
            insertChat("me", text);              
            $(this).val('');
            if (window.start_flag==1)
            {
                document.getElementById("from").value = text;
                document.getElementById("f").click(); 
                window.start_flag=0;
                // alert("Hi");
            }
            if (window.end_flag==1)
            {
                document.getElementById("to").value = text;
                document.getElementById("t").click(); 
                window.end_flag=0;
                document.getElementById("go").click();
                // alert("Hi");
            }


        }

    // var a =
    call_api_gateway_rider(text);
    // insertChat("you", reply);


  }
});
}
      var geocoder;
      var map;
      var address = "182 Claremont Avenue, New York, NY 10027";
      var to_address;
      var from_address;
      var path=[];

      function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          zoom: 12,
          center: {lat: -34.397, lng: 150.644}
        });
        
      }
      function addPinTo()
      {
        to_address = document.getElementById("to").value
        addPin(to_address)

      }
      function addPinFrom()
      {
        from_address = document.getElementById("from").value
        addPin(from_address)
      }


      function addPin(address)
      {
        
        geocoder = new google.maps.Geocoder();
        codeAddress(geocoder, map,address);

      }


      function codeAddress(geocoder, map, address) {
        geocoder.geocode({'address': address}, function(results, status) {
          if (status === 'OK') {
            map.setCenter(results[0].geometry.location);
            var lov = results[0].geometry.location;
            var di = {lat: lov.lat(), lng: lov.lng()};
            console.log(di);

            // console.log(results[0].geometry.location);
            // console.log(typeof(results[0].geometry.location));
            path.push(di);
            var marker = new google.maps.Marker({
              map: map,
              position: results[0].geometry.location
            });
          } else {
            alert('Geocode was not successful for the following reason: ' + status);
          }
        });
      }
      function LetsGo()
      {
        var flightPath = new google.maps.Polyline({
          path: path,
          geodesic: true,
          strokeColor: '#FF0000',
          strokeOpacity: 1.0,
          strokeWeight: 2
        });

        flightPath.setMap(map);
      }