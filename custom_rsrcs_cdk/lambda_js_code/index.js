// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

const aws = require('aws-sdk');
const connect = new aws.Connect();


exports.handler = async (event, context) => {
    console.log("EVENT: \n" + JSON.stringify(event, null, 2))
    
    var physical_id
    if (event.RequestType == "Create") {
        console.log("Received Event: " + event.RequestType);
        physical_id = await onCreateOrUpdate(event);
    }
    else if  (event.RequestType == "Update") {
        console.log("Received Event: " + event.RequestType);
        physical_id = await onCreateOrUpdate(event);
    } 
    else if  (event.RequestType == "Delete") {
        console.log("Received Event: " + event.RequestType);
        physical_id = await onDelete(event);

    } 
   
    /**
     * This function only does HAPPY PATH and it is not production ready
     * If you intend to use the function please add appropriate error handling 
     */
   send (event, context, SUCCESS,
                         "Association Established", event.LogicalResourceId)
    return event.LogicalResourceId;
};

/**
 * Create or Update function
 * We arent checking if existing storage association exist for Amazon Connect
 * To make this function fully functional implement that check before creating association
 * Thgis function will fail and rollback stack if existing storage association is present
 */
onCreateOrUpdate = async function(event) 
{
    console.log("== onCreateOrUpdate ==");
    
    var props = event.ResourceProperties;
    var instance_id = props.instance_id ;
    var resource_type = props.resource_type;
    var storage_type = props.storage_type; 
    var kinesis_arn = props.kinesis_arn;
    console.log("Received InstanceId: " + instance_id);
    
    var create_params;
    if (storage_type == "KINESIS_STREAM"){
        create_params = {
            InstanceId: instance_id,
            ResourceType: resource_type,
            StorageConfig: {
                StorageType: storage_type,
                "KinesisStreamConfig" : {
                    "StreamArn" : kinesis_arn
                }
            }
        };
    }
    else
    {
        create_params = {
            InstanceId: instance_id,
            ResourceType: resource_type,
            StorageConfig: {
                StorageType: storage_type,
                "KinesisFirehoseConfig" : {
                    "FirehoseArn" : kinesis_arn
                }
            }
        };
        
    }
    
    var paramsPrint = JSON.stringify(create_params, null, 2);
    console.log("Parameters: \n" +paramsPrint);
    
    const data = await connect.associateInstanceStorageConfig(create_params).promise();
    var str = JSON.stringify(data, null, 2);
    console.log(str);
    
    var physical_id = "EMPTY";
    
    if(data)
    {
        physical_id = data.AssociationId
    }
    
    return  {'PhysicalResourceId': physical_id};
}

/**
 * Delete Function
 */
onDelete = async function(event) 
{
    console.log("== onDelete ==");
    
    var props = event.ResourceProperties;
    var instance_id = props.instance_id ;
    var resource_type = props.resource_type;
    var storage_type = props.storage_type; 
    var kinesis_arn = props.kinesis_arn;
    console.log("[onDelete] Received InstanceId: " + instance_id);
    console.log("[onDelete] Received ResourceType: " + resource_type);
    
    
    const list_params = {
            InstanceId: instance_id,
            ResourceType: resource_type,
            MaxResults : "1"
        };
      
    const listData = await connect.listInstanceStorageConfigs(list_params).promise();
    var listDatastr = JSON.stringify(listData, null, 2);
    console.log("[onDelete] listInstanceStorageConfigs return: \n" +listDatastr);
    
    if(listData)
    {
        const associationId = listData.StorageConfigs[0].AssociationId;
        console.log("[onDelete] associationId to Delete: " +associationId);

        const dis_params = {
            AssociationId: associationId,
            InstanceId: instance_id,
            ResourceType: resource_type
        };
    
        const disData = await connect.disassociateInstanceStorageConfig(dis_params).promise();
        var disDataStr = JSON.stringify(disData, null, 2);
        console.log("[onDelete] disassociateInstanceStorageConfig return data is: /n" + disDataStr);
    
        return  {'PhysicalResourceId': event.LogicalResourceId};
        
    }
}

// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
 
SUCCESS = "SUCCESS";
FAILED = "FAILED";
 
send = function(event, context, responseStatus, responseData, physicalResourceId, noEcho) {
 
    var responseBody = JSON.stringify({
        Status: responseStatus,
        Reason: "See the details in CloudWatch Log Stream: " + context.logStreamName,
        PhysicalResourceId: physicalResourceId || context.logStreamName,
        StackId: event.StackId,
        RequestId: event.RequestId,
        LogicalResourceId: event.LogicalResourceId,
        NoEcho: noEcho || false,
        Data: responseData
    });
 
    console.log("Response body:\n", responseBody);
 
    var https = require("https");
    var url = require("url");
 
    var parsedUrl = url.parse(event.ResponseURL);
    var options = {
        hostname: parsedUrl.hostname,
        port: 443,
        path: parsedUrl.path,
        method: "PUT",
        headers: {
            "content-type": "",
            "content-length": responseBody.length
        }
    };
 
    var request = https.request(options, function(response) {
        console.log("Status code: " + response.statusCode);
        console.log("Status message: " + response.statusMessage);
        context.done();
    });
 
    request.on("error", function(error) {
        console.log("send(..) failed executing https.request(..): " + error);
        context.done();
    });
 
    request.write(responseBody);
    request.end();
}
