$(document).ready(function () {
  var currentRefresh = 0

  setInterval(UpdateTrade, 2000);
  function UpdateTrade() {
    $.post("/bot-data", {})
      .done(function (data) {

        updatedSpans("force_buy_notification", data.trade.forced_buy_applied, "badge bg-info text-dark");
        updatedSpans("skipping_trades", !data.trade.skipping_trades);
        updatedSpans("_limited_sell", data.trade._limited_sell, "badge bg-warning text-dark");
        updatedSpans("in_the_red", data.trade.in_the_red, "badge bg-danger");

        currentRefresh++;
        $("#profit_bar").attr('aria-valuenow', data.trade.current_normalized_profit).css('width', data.trade.current_normalized_profit + "%");
        $("#profit_bar").html(data.trade.current_normalized_profit + "%");

        current_round = Number(data.trade.counter);

        max_round = Number(data.trade.max_rounds);

        if (data.trade.skipping_trades) {
          var p = get_persenctage(data.trade.max_skip_trade, data.trade.skip_trade,0);
          $("#skiping_in_progress").attr('aria-valuenow', p).css('width', p + "%");
        }

        // if(!data.trade._forced_buy_applied){ $("#force_buy_notification:not([class*='d-none'])").addClass("d-none")} else{ $("#skiping_in_progress").removeClass("d-none")}
        progress = Math.round(current_round / max_round * 100);
        // if(progress == 30){
        //   showNotification({ 
        //     title: 'Title',
        //     message: 'Notification Message' 
        //   });
        // }
        // console.log(progress)
        $("#current_round_progress").attr('aria-valuenow', progress.toString()).css('width', progress.toString() + "%");


        $("#profit_bar").attr('aria-valuenow', data.trade.current_normalized_profit).css('width', data.trade.current_normalized_profit + "%");

        var init_asset = data.trade.asset.init_fiat_balance



        $("#init_fiat_balance").html("Init : " + USDString(data.trade.asset.init_overall_balance));
        $("#current_fiat_balance").html("Current : " + USDString(data.trade.asset.overall_balance));
        $("#last_fiat_balance").html("Last Sell : " + ShortString(data.trade.sell_price));
        try {
          $('#buy_nominee_table').empty();
          var count = 1
          data.trade.nominee.buy_list.slice(0, 5).forEach(buy => {
            $('#buy_nominee_table').append(

              '\
      <tr>\
      <th scope="row">'+ count + '</th>\
      <td>'+ buy.symbol + '</td>\
      <td>'+ ShortString(buy._current_price, 4) + '</td>\
      <td>'+ ShortString(buy.delta, 4) + '</td>\
      <td>'+ ShortString(buy.high_delta, 4) + '</td>\
      <td>'+ ShortString(buy.low_delta, 4) + '</td>\
      <td>'+ ShortString(buy.alpha, 4) + '</td>\
      <td>'+ ShortString(buy.beta, 4) + '</td>\
    </tr>');
            // if (count > 10) break;

            count++;

          });


          //tabels

          $('#available_for_trade').empty();
          $("#available_trades_number").html(data.trade._init_buy_nominee.length.toString() + " of " + data.trade.available_cryptos_to_trade.length.toString() + " available");
          var count = 1;
          data.trade._init_buy_nominee.slice(0, 5).forEach(buy => {
            $('#available_for_trade').append(

              '\
      <tr>\
      <th scope="row">'+ count + '</th>\
      <td>'+ buy.symbol + '</td>\
      <td>'+ ShortString(buy.delta, 4) + '</td>\
      <td>'+ ShortString(buy.bounce, 0) + '</td>\
      <td>'+ ShortString(buy.high_delta, 4) + '</td>\
      <td>'+ ShortString(buy.low_delta, 4) + '</td>\
      <td>'+ ShortString(buy.position, 0) + '%</td>\
      <td>'+ ShortString(buy.beta, 4) + '</td>\
      <td>'+ ShortString(buy.gamma, 4) + '</td>\
    </tr>');
            // if (count > 10) break;
            count++;

          });




          $('#current_assets').empty();
          var count = 1
          data.trade.asset.available_crypto_list.slice(0, 5).forEach(crypto => {
            $('#current_assets').append(

              '\
  <tr>\
  <th scope="row">'+ count + '</th>\
  <td>'+ crypto.symbol + '</td>\
  <td>'+ USDString(crypto._fiat_balance) + '</td>\
  </tr>');

            count++;

          });






          if (parseFloat(data.trade.skip_trade) == 1) { location.reload() }

          $("#sell_nominee").html(data.trade.nominee.sell.symbol +"  "+ ShortString(data.trade.nominee.sell.position,0) +"%");
          $("#best_buy").html(data.trade.nominee.best_buy.symbol);


        }
        catch {

        }

      }


      );
  }


});

// const showNotification = window.createNotification({
//     // close on click
//     closeOnClick: true,

//     // displays close button
//     displayCloseButton: false,

//     // nfc-top-left
//     // nfc-bottom-right
//     // nfc-bottom-left
//     positionClass: 'nfc-top-right',

//     // callback
//     onclick: false,

//     // timeout in milliseconds
//     showDuration: 3500,

//     // success, info, warning, error, and none
//     theme: 'success'
// });


function USDString(text) {
  return "$" + parseFloat(text).toFixed(2).toString();
}
function ShortString(text, digits = 2) {
  return parseFloat(text).toFixed(digits).toString();
}

function get_persenctage(max, current) {
  return ((parseFloat(current) / parseFloat(max)).toFixed(2) * 100).toString();
}

function updatedSpans(id, value, true_style = "badge bg-primary text-light", false_style = "badge bg-light text-dark") {
  var element = document.getElementById(id);
  s1 = false_style;
  s2 = true_style;
  if (!value) {
    s2 = false_style;
    s1 = true_style;
  }
  element.className = s1;
  element.className = s2;

}
