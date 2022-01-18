
# Welcome to your CDK Python project!

This is a blank project for Python development with CDK.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Deploying
To deploy CDK streaming for your own Amazon Connect instance you will need to run following command 
```
cdk deploy --parameters instanceId={YOUR-AMAZON-CONNECT-INSTANCE-ID}
           --parameters ctrStreamName={CTRStream} 
           --parameters agentStreamName={AgentStream}
```
instanceid parameter should look somethinglike this 2dg7a79f-94ed-4cbc-9217-f66id1e87424 

## IMPORTANT: 
By deafult stack will create Contact Trace Records stream  [ctrStreamName] as Kinesis stream. If you wish to use Kinesis Firehose delivery stream instead you can modify this behavior by going to cdk.json and adding  "ctr_stream_type": "KINESIS_FIREHOSE" as a parameter under "context".  

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
