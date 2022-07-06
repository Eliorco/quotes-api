<h1>Simplex Assignment</h1>
</br>
In order to run this service you'll need to:
</br>
1. build the image:
</br>
<code>
docker build . -t <<(image_tag_name)>> 
</code>
</br>
2. run the image
</br>
<code>
    docker run -d -p 3000:3000 <<(image_tag_name)>>       
</code>
<hr>
start sending the server requests:
</br>
<code>
curl http://localhost:3000/api/quote\?from_currency_code=USD&amount=1000&to_currency_code=ILS
</code>
</br>
response example:
</br>
<code>
{
    </br>
  "amount": 3540,</br>
  "currency_code": "USD",</br>
  "exchange_rate": 3.54,</br>
  "provider_name": "Exchangerate"</br>
}
</code>
</br>
