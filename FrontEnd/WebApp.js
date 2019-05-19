var me = {};

var you = {};

var post_url = "https://ajheyotkbj.execute-api.us-east-1.amazonaws.com/Prototype/chatbot"
var redirect_search = "https://s3.amazonaws.com/shareyourride/search.html"
function get_reply_message(text)
{
  var rep = text.split("text")[1].split("timestamp")[0];
  rep = rep.substring(4, rep.length-4);
  console.log(rep);
  insertChat("you",rep);
  if(rep=="Done")
  {
    window.location.replace(redirect_search);
  }

}

function getTokenID()
{
    var href = window.location.href;
    var parts = href.split('#')[1].split('&');
    var id_token = parts[0].split('=')[1];
    var access_id = parts[1].split('=')[1];
    var expires_in = parts[2].split('=')[1];
    var token_type = parts[3].split('=')[1];
    return id_token;

}

var status = prompt("For rider, press 1 else press 2", "1");

AWS.config.region = 'us-east-1';
var identityId = null;
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:245ff226-43d4-4def-94d6-59adc6568f7e',
    Logins: {
      'cognito-idp.us-east-1.amazonaws.com/us-east-1_QWKk0Nsje': getTokenID()
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

function call_api_gateway(inp)
{
    var params = {
  // This is where any modeled request parameters should be added.
  // The key is the parameter name, as it is defined in the API in API Gateway.
    };

    var body = {
      // This is where you define the body of the request,
      'body':inp,
      'userID':getTokenID(),

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
        
        apigClient.chatbotPost(params, body, additionalParams)
          .then(function (result) {
            // Add success callback code here.
            console.log(result.data.body);
            reply = result.data.body;
            // reply = result.data.body.messages[0].unstructured['text'];
            // return reply;
            console.log(reply);
            console.log("unable to go out why?");
            get_reply_message(reply);
            

          }).catch(function (result) {
            // reply = "Problem";
            // console.log("here2")
            // // Add error callback code here.
            // return reply;
          });

      });


    // return reply;

}




// var a;
// cognitoidentity.getId(params, function(err, data){
//           if(err) console.log(err, err.stack);
//           else {
//             var p = 
//             {
//               IdentityId: data['IdentityId'],
//               Logins:{
//                 "cognito-idp.us-east-1.amazonaws.com/us-east-1_QWKk0Nsje" : getTokenID()
//                       }
//             }
//           cognitoidentity.getCredentialsForIdentity(p, function(err,data1)
//             {
//               if (err) console.log(err, err.stack);
//               else 
//               {
//                   var apigClient = apigClientFactory.newClient({
//                     accessKey: data1.Credentials.AccessKeyId,
//                     secretKey: data1.Credentials.SecretKey,
//                     sessionToken: data1.Credentials.SessionToken,
//                     region : 'us-east-1'
//                     });
//                     a = apigClient;
//                     console.log("access ID : ", data1.Credentials.AccessKeyId," Secret key : ",data1.Credentials.SecretKey,"Session Token : ", data1.Credentials.SessionToken);
//                   //init api gateway with (apigClient);
//               }
//             }
//           )};
//     });

//'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'

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
    $("ul").empty();
}
function enter_chat(e){
    if(e.keyCode=13){
    alert("The paragraph was clicked.");
  console.log("haha");}

}
function Chat(){
resetChat();
console.log("haha")

var input = document.getElementById("input");
input.addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
   var text = $(this).val();
        if (text !== ""){
            insertChat("me", text);              
            $(this).val('');
        }
    // var a =
    call_api_gateway(text);
    // insertChat("you", reply);


  }
});
}
