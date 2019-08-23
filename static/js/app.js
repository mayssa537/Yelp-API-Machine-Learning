// event handler for the city submit button
d3.select('#citysubmit').on('click', cityAndOptions)

// fetch function to post city input & return category list & zipcodes via flask from the Yelp API
function cityAndOptions() {     
     d3.event.preventDefault();

     // converts city input to variable
     let inputElement = d3.select(".form-control")
     let inputValue = inputElement.property("value");

     // changes main page headline after location is submitted
     let headline = d3.select('#headline')
     headline.html(`Gathering options for ${inputValue}...`)
     
     // fetch request to post city input to flask
     fetch('/citytest', {
          method: 'POST',
          headers: {
               'Content-Type': 'application/json'
          },
          body: JSON.stringify({ inputValue })
     
     // awaits result from Yelp API and converts it to JSON (normally returns as an array)
     }).then(function (response) {          
          let optionsList = response.json()
          return optionsList          
     
     // callback function once result is returned to generate category list for multi-select options
     }).then(function (optionsList) {
          console.log('POST response: ');

          // updates headline, makes selection column headlines visible via css
          headline.html(`Select your options for ${inputValue}:`)
          document.getElementById('cat-select').style.visibility="visible"
          document.getElementById('zip-select').style.visibility="visible"
          document.getElementById('price-select').style.visibility="visible"          

          // vars to split the optionsList returned into separate arrays for categories & zip codes
          let categoryList = optionsList[0] 
          let zipCodeList = optionsList[1]                   

          // sorts categories alphabetically & zipcodes numerically in their respective elements
          categoryList = categoryList.sort()
          zipCodeList = zipCodeList.sort()          

          // loop to build category list, set element attributes and append to DOM
          let categorySelect = document.createElement('select');
          categorySelect.setAttribute("id", "select-category")
          categorySelect.setAttribute("multiple", "multiple")
          document.getElementById('select-options').appendChild(categorySelect);
          for (i=0; i < categoryList.length; i++) {
               let optionEntry = document.createElement('option');
               let optionText = document.createTextNode(categoryList[i])
               optionEntry.appendChild(optionText)
               document.getElementById('select-category').appendChild(optionEntry)
          }         
          
          // loop to build zip code list, set element attributes and append to DOM
          let zipSelect = document.createElement('select');
          zipSelect.setAttribute("id", "select-zip")          
          document.getElementById('zip-options').appendChild(zipSelect)
          for (i=0; i < zipCodeList.length; i++) {
               let zipOption = document.createElement('option');
               let zipText = document.createTextNode(zipCodeList[i])
               zipOption.appendChild(zipText)
               document.getElementById('select-zip').appendChild(zipOption)
          }

          // array of Yelp price points
          const priceArray = [1, 2, 3, 4]

          // loop to build price point list, set element attributes and append to DOM
          let priceSelect = document.createElement('select')
          priceSelect.setAttribute("id", "select-price")
          document.getElementById('price-options').appendChild(priceSelect)
          for (i=0; i < priceArray.length; i++) {
               let priceOption = document.createElement('option')
               let priceText = document.createTextNode(priceArray[i])
               priceOption.appendChild(priceText)
               document.getElementById('select-price').appendChild(priceOption)
          }

          // add button to submit user selected options
          let optionsButton = document.createElement('button')
          optionsButton.setAttribute("class", "btn btn-secondary")
          optionsButton.setAttribute("id", "optionssubmit")
          optionsButton.setAttribute("onclick","sendOptions()")
          optionsButton.innerHTML = "Submit"
          document.getElementById('options-button').appendChild(optionsButton)
     })

     // catch any errors that result from the Yelp API call
     .catch(function(err) {
          headline.html('The Yelp API had a brain fart. Press "Start Over" to try again')
     })
}

// fetch request to send user selected options to python and return machine learning result
function sendOptions() {
     event.preventDefault();

     // convert selected options to their respective values via jQuery
     let catSelect = $('#select-category').val()
     let zipSelect = $('#select-zip').val()
     let priceSelect = $('#select-price').val()
     fetch('/useroptions', {
          method: 'POST',
          headers: {
               'Content-Type': 'application/json'
          },
          body: JSON.stringify([ catSelect, zipSelect, priceSelect ])
     }).then(function(response) {
          let optionsResponse = response.json()
          return optionsResponse
     }).then(function(optionsResponse) {

          // makes result div headline visible via css
          document.getElementById('final-result').style.visibility="visible"
          
          // push prediction result to html
          let analysisResult = document.createElement('div')
          analysisResult.setAttribute("class", "card-body")
          analysisResult.setAttribute("id", "result")
          document.getElementById('response-card').appendChild(analysisResult)
          let p = document.createElement('p')
          p.setAttribute("class", "card-text")
          let result = document.createTextNode(`Prediction: ${optionsResponse}`)
          p.appendChild(result)
          document.getElementById('result').appendChild(p)

          // add button to submit user selected options
          let mapButton = document.createElement('button')
          mapButton.setAttribute("class", "btn btn-secondary")
          mapButton.setAttribute("id", "makemap")
          mapButton.setAttribute("onclick", "location.href='/map'")
          mapButton.innerHTML = "Get Map"
          document.getElementById('map-button').appendChild(mapButton)
     })

     // catch any errors that result from user selected options
     .catch(function(err) {
          console.log(err)
          document.getElementById('response-card').innerHTML = `Hmmmm... something went wrong.`
     })     
}

// click handler to reload page and start new API search from navbar
d3.select('#do-over').on('click', function() {
     window.location.reload()
})