/* JS Document */

/******************************

 [Table of Contents]

 1. Vars and Inits
 2. Set Header
 3. Init Search
 4. Init Menu
 5. Init Quantity


 ******************************/

$(document).ready(function () {
    "use strict";

    /*

    1. Vars and Inits

    */

    var header = $('.header');
    var hambActive = false;
    var menuActive = false;

    setHeader();

    $(window).on('resize', function () {
        setHeader();
    });

    $(document).on('scroll', function () {
        setHeader();
    });

    initSearch();
    initMenu();
    initQuantity();
    initShippingMethod();

    /*

    2. Set Header

    */

    function setHeader() {
        if ($(window).scrollTop() > 100) {
            header.addClass('scrolled');
        } else {
            header.removeClass('scrolled');
        }
    }

    /*

    3. Init Search

    */

    function initSearch() {
        if ($('.search').length && $('.search_panel').length) {
            var search = $('.search');
            var panel = $('.search_panel');

            search.on('click', function () {
                panel.toggleClass('active');
            });
        }
    }

    /*

    4. Init Menu

    */

    function initMenu() {
        if ($('.hamburger').length) {
            var hamb = $('.hamburger');

            hamb.on('click', function (event) {
                event.stopPropagation();

                if (!menuActive) {
                    openMenu();

                    $(document).one('click', function cls(e) {
                        if ($(e.target).hasClass('menu_mm')) {
                            $(document).one('click', cls);
                        } else {
                            closeMenu();
                        }
                    });
                } else {
                    $('.menu').removeClass('active');
                    menuActive = false;
                }
            });

            //Handle page menu
            if ($('.page_menu_item').length) {
                var items = $('.page_menu_item');
                items.each(function () {
                    var item = $(this);

                    item.on('click', function (evt) {
                        if (item.hasClass('has-children')) {
                            evt.preventDefault();
                            evt.stopPropagation();
                            var subItem = item.find('> ul');
                            if (subItem.hasClass('active')) {
                                subItem.toggleClass('active');
                                TweenMax.to(subItem, 0.3, {height: 0});
                            } else {
                                subItem.toggleClass('active');
                                TweenMax.set(subItem, {height: "auto"});
                                TweenMax.from(subItem, 0.3, {height: 0});
                            }
                        } else {
                            evt.stopPropagation();
                        }
                    });
                });
            }
        }
    }

    function openMenu() {
        var fs = $('.menu');
        fs.addClass('active');
        hambActive = true;
        menuActive = true;
    }

    function closeMenu() {
        var fs = $('.menu');
        fs.removeClass('active');
        hambActive = false;
        menuActive = false;
    }

    /*

    5. Init Quantity

    */


    function initQuantity() {
        // Handle product quantity input
        if ($('.product_quantity').length) {
            var input = $('#quantity_input');
            var incButton = $('#quantity_inc_button');
            var decButton = $('#quantity_dec_button');
            var priceEl = document.getElementsByClassName('cart_total_value ml-auto');
            var sum_priceEl = document.getElementsByClassName('cart_item_total')[0];
            try {
                var delta_value = document.getElementsByClassName('cart_item_price')[0].innerText;
            } catch (TypeError) {

            }
            var originalVal;
            var endVal;
            var endPriceVAl;
            incButton.on('click', function () {
                originalVal = input.val();
                endVal = parseFloat(originalVal) + 1;
                if (sum_priceEl) {
                    for (let count = 0; count < priceEl.length; count = count + 2) {
                        endPriceVAl = parseFloat(priceEl[count].innerText.replace('$', '')) + parseFloat(delta_value.replace('$', ''))
                        priceEl[count].innerText = ('$'.concat(endPriceVAl.toString()))
                        sum_priceEl.innerText = ('$'.concat(endPriceVAl.toString()))
                    }
                    sum_priceEl.innerText = '$'.concat((parseFloat(delta_value.replace('$', '')) * endVal).toString())
                }
                input.val(endVal);
            });

            decButton.on('click', function () {
                originalVal = input.val();
                if (originalVal > 1) {
                if (sum_priceEl) {
                    for (let count = 0; count < priceEl.length; count = count + 2) {
                        endPriceVAl = parseFloat(priceEl[count].innerText.replace('$', '')) - parseFloat(delta_value.replace('$', ''))
                        priceEl[count].innerText = ('$'.concat(endPriceVAl.toString()))
                        sum_priceEl.innerText = ('$'.concat(endPriceVAl.toString()))
                    }
                }
                    endVal = parseFloat(originalVal) - 1;
                    sum_priceEl.innerText = '$'.concat((parseFloat(delta_value.replace('$', '')) * endVal).toString())
                    input.val(endVal);
                }
            });
        }
    }

    function initShippingMethod() {
        let standardMethod = false
        let nextDayMethod = false
        // let elements = document.getElementsByClassName('row cart_items_row')
        // for (let counter = 0; counter < 1; counter++){
        //     let basicEl = elements[counter].getElementsByClassName('cart_item d-flex flex-lg-row flex-column align-items-lg-center align-items-start justify-content-start')
        //     for (let count = 0; count < basicEl.length; count++){
        //         let cur_el = basicEl[count].getElementsByClassName('product_quantity clearfix')[0].getElementsByTagName('input')[0]
        //         console.log()
        //     }
        //
        // }
        //
        // input[type='radio']
        //
        $("input[type='radio']").click(function () {
            if ($('.delivery').length > 0) {
                let shippingData = document.getElementsByClassName('cart_total_value ml-auto');
                let counter = 3;
                for (let i = 0; i < counter; i++) {
                    let element = document.getElementsByClassName('delivery_option clearfix')[i]
                    for (let count = 0; count < element.childElementCount; count++) {
                        if (element.children[count].checked) {
                            let cur_element = element.children.item(2).innerText.toString()
                            if (cur_element !== 'Free') {
                                let el = parseFloat(cur_element.replace('$', ''))
                                shippingData[1].innerText = '$'.concat(el.toString())
                                shippingData[2].innerText = '$'.concat((parseFloat(shippingData[0].innerText.toString().replace('$', '')) + parseFloat(el.toString().replace('$', ''))).toString())
                                if (parseFloat(shippingData[1].innerText.toString().replace('$', '')) < 2) {
                                    standardMethod = true
                                    nextDayMethod = false
                                } else {
                                    nextDayMethod = true
                                    standardMethod = false
                                }
                            } else {
                                shippingData[1].innerText = 'Free'
                                if (standardMethod === true) {
                                    shippingData[2].innerText = '$'.concat((parseFloat(shippingData[2].innerText.toString().replace('$', '')) - 1.99).toString())
                                    standardMethod = false;
                                    nextDayMethod = false;
                                }
                                if (nextDayMethod === true) {
                                    console.log((parseFloat(shippingData[2].innerText.toString().replace('$', ''))))
                                    shippingData[2].innerText = '$'.concat((parseFloat(shippingData[2].innerText.toString().replace('$', '')) - 4.99).toString())
                                    standardMethod = false;
                                    nextDayMethod = false;
                                }
                            }
                        }
                    }
                }
            }
        })
    }

});