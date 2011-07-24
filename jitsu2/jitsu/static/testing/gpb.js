
(function($) {
    $.extend({
        progressBar: new function() {

            this.defaults = {
                increment    : 2,
                speed        : 15,
                showText    : true,                                            // show text with percentage in next to the progressbar? - default : true
                width        : 120,                                            // Width of the progressbar - don't forget to adjust your image too!!!
                bgColor : "#ff9999",
                height        : 20                                            // Height of the progressbar - don't forget to adjust your image too!!!
            };
            
            /* public methods */
            this.construct = function(amount) {
                var width = 400;
                var height = 24;
                
                var amount = parseInt(amount);
                var rest = 100 - parseInt(amount);
                
                
                this.html("");
                
                var bar = document.createElement('table');
                bar.cellSpacing = 0;
                
                var row = document.createElement('tr');
                var left = document.createElement('td');
                var right = document.createElement('td');
                
                this._bar = bar;
                this._row = row;
                this._left = left;
                this._right = right;
                
                $(bar).css('border', '1px solid black');
            
                    if (amount == 100) {
//                        $(left).html(amount + "%");
//                        $(right).html(rest + "%");
                        $(row).append(left);
                    } else if (amount == 0) {
//                        $(left).html("0%");
//                        $(right).html("0%");
                        $(row).append(right);
                    }
                    else {
//                        $(left).html(amount + "%");
//                        $(right).html(rest + "%");
                        $(row).append(left);
                        $(row).append(right);
                    }                
                $(bar).append(row);
                
                $(left).css("width", amount + "%");
                $(left).css("background-color", "#ff9999");
                $(left).css("background-image", "url(test2.png)");
                $(left).css("text-align", 'center');
                $(left).css("font-family", 'courier');
                $(left).css("font-size", '9px');
                $(left).css("color", "white");
                $(right).css("width", rest + "%");
                $(right).css("background-color", "#dddddd");
                $(right).css("text-align", 'center');
                $(right).css("font-family", 'courier');
                $(right).css("font-size", '9px');
                
                $(left).css("height", height + "px");
                $(right).css("height", height + "px");

                $(bar).css("width", width + "px");
                $(bar).css("height", height + "px");
                $(bar).css("padding", "0px");
                $(bar).css("margin", "0px");

                $(this).append(bar);
            }
            
        }   
    });
    
        
    $.fn.extend({
        progressBar: $.progressBar.construct
    });
    
})(jQuery);