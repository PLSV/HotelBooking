const config={
    cognito:{
        identityPoolId:"us-east-2_Mb6ec4kay",
        cognitoDomain:"https://hotel-vasan.auth.us-east-2.amazoncognito.com",
        appId:"3jkvt8duh3l8gn456plo773og7"
    }
}

var cognitoApp={
    auth:{},
    Init: function()
    {

        var authData = {
            ClientId : config.cognito.appId,
            AppWebDomain : config.cognito.cognitoDomain,
            TokenScopesArray : ['email', 'openid','profile'],
            RedirectUriSignIn : 'http://localhost:8080/hotel_pavan/',
            RedirectUriSignOut : 'http://localhost:8080/hotel_pavan/',
            UserPoolId : config.cognito.identityPoolId, 
            AdvancedSecurityDataCollectionFlag : false,
                Storage: null
        };

        cognitoApp.auth = new AmazonCognitoIdentity.CognitoAuth(authData);
        cognitoApp.auth.userhandler = {
            onSuccess: function(result) {

            },
            onFailure: function(err) {
            }
        };
    }
}