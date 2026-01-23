(function ($) {
  "use strict";
  
  // ==========================================
  //      Start Document Ready function
  // ==========================================
  $(document).ready(function () {
    
  // ============== Mobile Menu Sidebar & Offcanvas Js Start ========
  $('.toggle-mobileMenu').on('click', function () {
    $('.mobile-menu').addClass('active');
    $('.side-overlay').addClass('show');
    $('body').addClass('scroll-hide-sm');
  }); 

  $('.close-button, .side-overlay').on('click', function () {
    $('.mobile-menu').removeClass('active');
    $('.side-overlay').removeClass('show');
    $('body').removeClass('scroll-hide-sm');
  }); 
  // ============== Mobile Menu Sidebar & Offcanvas Js End ========
  
  // ============== Mobile Nav Menu Dropdown Js Start =======================
  var windowWidth = $(window).width(); 
  
  $('.has-submenu').on('click', function () {
    var thisItem = $(this); 
    
    if(windowWidth < 992) {
      if(thisItem.hasClass('active')) {
        thisItem.removeClass('active')
      } else {
        $('.has-submenu').removeClass('active')
        $(thisItem).addClass('active')
      }
      
      var submenu = thisItem.find('.nav-submenu');
      
      $('.nav-submenu').not(submenu).slideUp(300);
      submenu.slideToggle(300);
    }
    
  });
  // ============== Mobile Nav Menu Dropdown Js End =======================
    
  // ===================== Scroll Back to Top Js Start ======================
  var progressPath = document.querySelector('.progress-wrap path');
  if (progressPath) {
    var pathLength = progressPath.getTotalLength();
    progressPath.style.transition = progressPath.style.WebkitTransition = 'none';
    progressPath.style.strokeDasharray = pathLength + ' ' + pathLength;
    progressPath.style.strokeDashoffset = pathLength;
    progressPath.getBoundingClientRect();
    progressPath.style.transition = progressPath.style.WebkitTransition = 'stroke-dashoffset 10ms linear';
    var updateProgress = function () {
      var scroll = $(window).scrollTop();
      var height = $(document).height() - $(window).height();
      var progress = pathLength - (scroll * pathLength / height);
      progressPath.style.strokeDashoffset = progress;
    }
    updateProgress();
    $(window).scroll(updateProgress);
    var offset = 50;
    var duration = 550;
    jQuery(window).on('scroll', function() {
      if (jQuery(this).scrollTop() > offset) {
        jQuery('.progress-wrap').addClass('active-progress');
      } else {
        jQuery('.progress-wrap').removeClass('active-progress');
      }
    });
    jQuery('.progress-wrap').on('click', function(event) {
      event.preventDefault();
      jQuery('html, body').animate({scrollTop: 0}, duration);
      return false;
    })
  }
  // ===================== Scroll Back to Top Js End ======================

  // ========================== add active class to ul>li top Active current page Js Start =====================
  function dynamicActiveMenuClass(selector) {
    let FileName = window.location.pathname.split("/").reverse()[0];

    selector.find("li").each(function () {
      let anchor = $(this).find("a");
      if ($(anchor).attr("href") == FileName) {
        $(this).addClass("activePage");
      }
    });
    // if any li has activePage element add class
    selector.children("li").each(function () {
      if ($(this).find(".activePage").length) {
        $(this).addClass("activePage");
      }
    });
    // if no file name return
    if ("" == FileName) {
      selector.find("li").eq(0).addClass("activePage");
    }
  }
  if ($('ul').length) {
    dynamicActiveMenuClass($('ul'));
  }
  // ========================== add active class to ul>li top Active current page Js End =====================

  
  // ========================== Select2 Js Start =================================
  $(document).ready(function() {
    $('.js-example-basic-single').select2();
});
  // ========================== Select2 Js End =================================

  
  // ========================== Select2 Js End =================================
  $('.search-icon').on('click', function () {
    $('.search-box').addClass('active'); 
  }); 
  $('.search-box__close').on('click', function () {
    $('.search-box').removeClass('active'); 
  }); 
  // ========================== Select2 Js End =================================

  
  // ========================== Category Dropdown Responsive Js Start =================================
  $('.responsive-dropdown .has-submenus-submenu').on('click', function () {

    var windowWidth = $(window).width(); 
    if(windowWidth < 992) { 
      if ($(this).hasClass('active')) {
        $(this).removeClass('active');
        $(this).children('.submenus-submenu').slideUp();
      } else {
        $('.responsive-dropdown .has-submenus-submenu').removeClass('active');
        $('.responsive-dropdown .has-submenus-submenu').children('.submenus-submenu').slideUp();
  
        $(this).addClass('active');
        $(this).children('.submenus-submenu').slideDown();
      }
    }
  });
  // ========================== Category Dropdown Responsive Js End =================================

  // ========================== On Click Category menu show Js Start =================================
  $('.category__button').on('click', function () {    
    $('.responsive-dropdown').addClass('active'); 
    $('.side-overlay').addClass('show');
    $('body').addClass('scroll-hide-sm');
  }); 
  $('.side-overlay, .close-responsive-dropdown').on('click', function () {    
    $('.responsive-dropdown').removeClass('active'); 
    $('.side-overlay').removeClass('show');
    $('body').removeClass('scroll-hide-sm');
  }); 
  // ========================== On Click Category menu show Js End =================================

  
  // ========================== Set Language in dropdown Js Start =================================
  $('.selectable-text-list li').each(function () {
    var thisItem = $(this); 

    thisItem.on('click', function () {
      const listText = thisItem.text(); 
      var item = thisItem.parent().parent().find('.selected-text').text(listText); 
    }); 
  }); 
  // ========================== Set Language in dropdown Js End =================================

  
  // ========================= Banner Slider Js Start ==============
  $('.banner-slider').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: false,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#banner-next',
    prevArrow: '#banner-prev',
    responsive: [
      {
        breakpoint: 767,
        settings: {
          slidesToShow: 1,
        }
      }
    ]
  });  
  // ========================= Banner Slider Js End ===================


   // ========================= hot deals Slider Js Start ==============
   $('.feature-item-wrapper').slick({
    slidesToShow: 10,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#feature-item-wrapper-next',
    prevArrow: '#feature-item-wrapper-prev',
    responsive: [
      {
        breakpoint: 1699,
        settings: {
          slidesToShow: 9,
        }
      },
      {
        breakpoint: 1599,
        settings: {
          slidesToShow: 8,
        }
      },
      {
        breakpoint: 1399,
        settings: {
          slidesToShow: 6,
        }
      },
      {
        breakpoint: 992,
        settings: {
          slidesToShow: 5,
        }
      },
      {
        breakpoint: 768,
        settings: {
          slidesToShow: 4,
        }
      },
      {
        breakpoint: 575,
        settings: {
          slidesToShow: 3,
        }
      },
      {
        breakpoint: 424,
        settings: {
          slidesToShow: 2,
        }
      },
      {
        breakpoint: 359,
        settings: {
          slidesToShow: 1,
        }
      },
    ]
  });  
  // ========================= hot deals Slider Js End ===================

  
  // ========================= Banner Slider Js Start ==============
  $('.banner-item-two__slider').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: false,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: true,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#banner-next',
    prevArrow: '#banner-prev',
    responsive: [
      {
        breakpoint: 767,
        settings: {
          slidesToShow: 1,
        }
      }
    ]
  });  
  // ========================= Banner Slider Js End ===================

  
  // ========================= flash Sale Four Slider Js Start ==============
  $('.flash-sales__slider').slick({
    slidesToShow: 2,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#flash-next',
    prevArrow: '#flash-prev',
    responsive: [
      {
        breakpoint: 991,
        settings: {
          slidesToShow: 1,
          arrows: false,
        }
      }
    ]
  });  
  // ========================= flash Sale Four Slider Js End ==================
    
  // ========================= hot deals Slider Js Start ==============
  $('.hot-deals-slider').slick({
    slidesToShow: 4,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#deals-next',
    prevArrow: '#deals-prev',
    responsive: [
      {
        breakpoint: 1399,
        settings: {
          slidesToShow: 3,
          arrows: false,
        }
      },
      {
        breakpoint: 1199,
        settings: {
          slidesToShow: 2,
          arrows: false,
        }
      },
      {
        breakpoint: 575,
        settings: {
          slidesToShow: 1,
          arrows: false,
        }
      },
    ]
  });  
  // ========================= hot deals Slider Js End ===================
    
    
  // ========================= hot deals Slider Js Start ==============
  $('.deals-week-slider').slick({
    slidesToShow: 6,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#deal-week-next',
    prevArrow: '#deal-week-prev',
    responsive: [
      {
        breakpoint: 1599,
        settings: {
          slidesToShow: 5,
          arrows: false,
        }
      },
      {
        breakpoint: 1399,
        settings: {
          slidesToShow: 3,
          arrows: false,
        }
      },
      {
        breakpoint: 1199,
        settings: {
          slidesToShow: 2,
          arrows: false,
        }
      },
      {
        breakpoint: 575,
        settings: {
          slidesToShow: 1,
          arrows: false,
        }
      },
    ]
  });  
  // ========================= hot deals Slider Js End ===================
    

  // ========================= hot deals Slider Js Start ==============
  $('.top-selling-product-slider').slick({
    slidesToShow: 4,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#top-selling-next',
    prevArrow: '#top-selling-prev',
    responsive: [
      {
        breakpoint: 1399,
        settings: {
          slidesToShow: 3,
          arrows: false,
        }
      },
      {
        breakpoint: 1199,
        settings: {
          slidesToShow: 2,
          arrows: false,
        }
      },
      {
        breakpoint: 575,
        settings: {
          slidesToShow: 1,
          arrows: false,
        }
      },
    ]
  });  
  // ========================= hot deals Slider Js End ===================

  
  // ========================= hot deals Slider Js Start ==============
  $('.organic-food__slider').slick({
    slidesToShow: 6,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#organic-next',
    prevArrow: '#organic-prev',
    responsive: [
      {
        breakpoint: 1599,
        settings: {
          slidesToShow: 6,
          arrows: false,
        }
      },
      {
        breakpoint: 1399,
        settings: {
          slidesToShow: 4,
          arrows: false,
        }
      },
      {
        breakpoint: 992,
        settings: {
          slidesToShow: 3,
          arrows: false,
        }
      },
      {
        breakpoint: 575,
        settings: {
          slidesToShow: 2,
          arrows: false,
        }
      },
      {
        breakpoint: 424,
        settings: {
          slidesToShow: 1,
          arrows: false,
        }
      },
    ]
  });  
  // ========================= hot deals Slider Js End ===================

  
  // ========================= New arrival Slider Js Start ==============
  $('.new-arrival__slider').slick({
    slidesToShow: 6,
    slidesToScroll: 1,
    autoplay: false,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#new-arrival-next',
    prevArrow: '#new-arrival-prev',
    responsive: [
      {
        breakpoint: 1599,
        settings: {
          slidesToShow: 6,
          arrows: false,
        }
      },
      {
        breakpoint: 1399,
        settings: {
          slidesToShow: 4,
          arrows: false,
        }
      },
      {
        breakpoint: 992,
        settings: {
          slidesToShow: 3,
          arrows: false,
        }
      },
      {
        breakpoint: 575,
        settings: {
          slidesToShow: 2,
          arrows: false,
        }
      },
      {
        breakpoint: 424,
        settings: {
          slidesToShow: 1,
          arrows: false,
        }
      },
    ]
  });  
  // ========================= New arrival Slider Js End ===================

  
  // ========================= hot deals Slider Js Start ==============
  $('.short-product-list').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    prevArrow: '<button type="button" class="slick-prev border border-gray-100 w-30 h-30 bg-transparent rounded-pill position-absolute hover-bg-main-600 hover-text-white hover-border-main-600 transition-1"><i class="ph ph-caret-left"></i></button>',
    nextArrow: '<button type="button" class="slick-next border border-gray-100 w-30 h-30 bg-transparent rounded-pill position-absolute hover-bg-main-600 hover-text-white hover-border-main-600 transition-1"><i class="ph ph-caret-right"></i></button>',
  });  
  
// ========================= hot deals Slider Js End ===================

  
  // ========================= hot deals Slider Js Start ==============
  $('.brand-slider').slick({
    slidesToShow: 8,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#brand-next',
    prevArrow: '#brand-prev',
    responsive: [
      {
        breakpoint: 1599,
        settings: {
          slidesToShow: 7,
          arrows: false,
        }
      },
      {
        breakpoint: 1399,
        settings: {
          slidesToShow: 6,
          arrows: false,
        }
      },
      {
        breakpoint: 992,
        settings: {
          slidesToShow: 5,
          arrows: false,
        }
      },
      {
        breakpoint: 575,
        settings: {
          slidesToShow: 4,
          arrows: false,
        }
      },
      {
        breakpoint: 424,
        settings: {
          slidesToShow: 3,
          arrows: false,
        }
      },
      {
        breakpoint: 359,
        settings: {
          slidesToShow: 2,
          arrows: false,
        }
      },
    ]
  });  
  // ========================= hot deals Slider Js End ===================

  
  // ========================= Category Dropdown Two Js Start ===============================
  $('.category-two .category__button').on('click', function () {
    $('.category-two .category__button').toggleClass('active')
    $('.responsive-dropdown.style-two').addClass('active').slideToggle(400); 
  }); 
  // ========================= Category Dropdown Two Js End ===============================
  
  
  // ========================= Featured Products Slider Js Start ==============
  $('.featured-product-slider').slick({
    slidesToShow: 2,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#featured-products-next',
    prevArrow: '#featured-products-prev',
    responsive: [
      {
        breakpoint: 991,
        settings: {
          slidesToShow: 1,
          arrows: false,
        }
      }
    ]
  });  
  // ========================= Featured Products Slider Js End ==================

  
  // ========================= hot deals Slider Js Start ==============
  $('.recommended-slider').slick({
    slidesToShow: 4,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#recommended-next',
    prevArrow: '#recommended-prev',
    responsive: [
      {
        breakpoint: 1399,
        settings: {
          slidesToShow: 3,
          arrows: false,
        }
      },
      {
        breakpoint: 1199,
        settings: {
          slidesToShow: 2,
          arrows: false,
        }
      },
      {
        breakpoint: 575,
        settings: {
          slidesToShow: 1,
          arrows: false,
        }
      },
    ]
  });  
  // ========================= hot deals Slider Js End ===================
  
  // ========================= hot deals Slider Js Start ==============
  $('.vendor-card__list.style-two').slick({
    slidesToShow: 4,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#vendor-next',
    prevArrow: '#vendor-prev',
  });  
  // ========================= hot deals Slider Js End ===================
  
  
  // ========================= hot deals Slider Js Start ==============
  $('.top-brand__slider').slick({
    slidesToShow: 8,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    speed: 1500,
    dots: false,
    pauseOnHover: true,
    arrows: true,
    draggable: true,
    rtl: $('html').attr('dir') === 'rtl' ? true : false,
    speed: 900,
    infinite: true,
    nextArrow: '#topBrand-next',
    prevArrow: '#topBrand-prev',
    responsive: [
      {
        breakpoint: 1599,
        settings: {
          slidesToShow: 7,
          arrows: false,
        }
      },
      {
        breakpoint: 1399,
        settings: {
          slidesToShow: 6,
          arrows: false,
        }
      },
      {
        breakpoint: 992,
        settings: {
          slidesToShow: 5,
          arrows: false,
        }
      },
      {
        breakpoint: 575,
        settings: {
          slidesToShow: 4,
          arrows: false,
        }
      },
      {
        breakpoint: 424,
        settings: {
          slidesToShow: 3,
          arrows: false,
        }
      },
      {
        breakpoint: 359,
        settings: {
          slidesToShow: 2,
          arrows: false,
        }
      },
    ]
  });  
  // ========================= hot deals Slider Js End ===================

  
  // ========================= Product Details Thumbs Slider Js Start ===================
  $('.product-details__thumb-slider').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false,
    fade: true,
    asNavFor: '.product-details__images-slider'
  });

  $('.product-details__images-slider').slick({
    slidesToShow: 4,
    slidesToScroll: 1,
    asNavFor: '.product-details__thumb-slider',
    dots: false,
    arrows: false,
    focusOnSelect: true
  });
  // ========================= Product Details Thumbs Slider Js End ===================

  
  // ========================= Increment & Decrement Js Start ===================
  var minus = $('.quantity__minus');
  var plus = $('.quantity__plus');

  $(plus).on('click', function () {
    var input = $(this).siblings('.quantity__input');
    var value = input.val(); 
    value++;
    input.val(value); 
  }); 

  $(minus).on('click', function () {
    var input = $(this).siblings('.quantity__input');
    var value = input.val(); 
    if(value > 1) {
      value--;
    }
    input.val(value); 
  }); 
  // ========================= Increment & Decrement Js End ===================

  
  // ========================= Color List Js Start ===================
  $('.color-list__button').on('click', function () {
    $('.color-list__button').removeClass('border-gray-900'); 

    if(!$(this).hasClass('border-gray-900')) {
      $(this).addClass('border-gray-900');
      $(this).removeClass('border-gray-50');
    } else {
      $(this).removeClass('border-gray-900');
      $(this).addClass('border-gray-50');
    };
  }); 
  // ========================= Color List Js End ===================

  // ========================== Range Slider Js Start =====================
  $(function() {
    var $slider = $("#slider-range");
    if (!$slider.length || !$.fn.slider || $slider.hasClass("ui-slider")) {
        return;
    }

    var min = parseFloat($slider.data("min"));
    var max = parseFloat($slider.data("max"));
    var step = parseFloat($slider.data("step"));
    var prefix = $slider.data("prefix") || "$";
    var valuesRaw = ($slider.data("values") || "").toString().split(",");
    var values = valuesRaw.length === 2 ? [parseFloat(valuesRaw[0]), parseFloat(valuesRaw[1])] : [min, max];

    if (isNaN(min)) min = 0;
    if (isNaN(max)) max = 25;
    if (isNaN(step) || step <= 0) step = 1;
    if (isNaN(values[0])) values[0] = min;
    if (isNaN(values[1])) values[1] = max;

    var $minInput = $("#min_price");
    var $maxInput = $("#max_price");

    var formatValue = function (val) {
        return prefix + val;
    };

    var updateInputs = function (rangeValues) {
        if ($minInput.length) $minInput.val(rangeValues[0]);
        if ($maxInput.length) $maxInput.val(rangeValues[1]);
    };

    var triggerHtmxFilter = function () {
        var changeEvent = new Event("change", { bubbles: true });
        if ($minInput.length) $minInput[0].dispatchEvent(changeEvent);
        if ($maxInput.length) $maxInput[0].dispatchEvent(changeEvent);
    };

    var updateSlider = function () {
        var minVal = $minInput.length ? parseFloat($minInput.val()) : min;
        var maxVal = $maxInput.length ? parseFloat($maxInput.val()) : max;

        if (isNaN(minVal)) minVal = min;
        if (isNaN(maxVal)) maxVal = max;

        minVal = Math.max(min, Math.min(minVal, max));
        maxVal = Math.max(min, Math.min(maxVal, max));

        if (minVal > maxVal) {
            var swap = minVal;
            minVal = maxVal;
            maxVal = swap;
        }

        $slider.slider("values", [minVal, maxVal]);
        updateInputs([minVal, maxVal]);
        $("#amount").val(formatValue(minVal) + " - " + formatValue(maxVal));
    };

    $slider.slider({
        range: true,
        min: min,
        max: max,
        step: step,
        values: values,
        slide: function( event, ui ) {
            updateInputs(ui.values);
            $("#amount").val(formatValue(ui.values[0]) + " - " + formatValue(ui.values[1]));
        },
        stop: function (event, ui) {
            updateInputs(ui.values);
            $("#amount").val(formatValue(ui.values[0]) + " - " + formatValue(ui.values[1]));
            triggerHtmxFilter();
        }
    });
    $("#amount").val(formatValue($slider.slider("values", 0)) +
        " - " + formatValue($slider.slider("values", 1)));
    updateInputs([$slider.slider("values", 0), $slider.slider("values", 1)]);

    if ($minInput.length) $minInput.on("change keyup", updateSlider);
    if ($maxInput.length) $maxInput.on("change keyup", updateSlider);
  });
  // ========================== Range Slider Js End =====================

  
  // ========================== List Grid Js Start ================================
  $('.list-btn').on('click', function () {
    $('.grid-btn').addClass('border-gray-100'); 
    $('.grid-btn').removeClass('border-main-600 text-white bg-main-600'); 
    $('.list-grid-wrapper').removeClass('list-view'); 
    
    $(this).removeClass('border-gray-100'); 
    $(this).addClass('border-main-600 text-white bg-main-600'); 
    $('.list-grid-wrapper').addClass('list-view'); 
  }); 

  $('.grid-btn').on('click', function () {
    $('.list-btn').addClass('border-gray-100'); 
    $('.list-btn').removeClass('border-main-600 text-white bg-main-600'); 
    $('.list-grid-wrapper').removeClass('list-view'); 

    $(this).removeClass('border-gray-100'); 
    $(this).addClass('border-main-600 text-white bg-main-600'); 
  }); 
  // ========================== List Grid Js End ================================

  
  // ========================== Shop Sidebar Js Start ================================
  $('.sidebar-btn').on('click', function () {
    $(this).addClass('bg-main-600 text-white');
    $('.shop-sidebar').addClass('active');
    $('.side-overlay').addClass('show');
    $('body').addClass('scroll-hide-sm'); 
  }); 

  $('.side-overlay, .shop-sidebar__close').on('click', function () {
    $('.sidebar-btn').removeClass('bg-main-600 text-white');
    $('.shop-sidebar').removeClass('active');
    $('.side-overlay').removeClass('show');
    $('body').removeClass('scroll-hide-sm');
  }); 
  // ========================== Shop Sidebar Js End ================================

  
  // ========================== Remove Tr Js Start ================================
  $('.remove-tr-btn').on('click', function () {
    $(this).closest('tr').addClass('d-none')
  }); 
  // ========================== Remove Tr Js End ================================

  
  // ========================== Checkout Payment Method Js Start ================================
  $('.payment-item .form-check-input:checked').closest('.payment-item').find('.payment-item__content').show();

  $('.payment-item .form-check-input').on('change', function () {
      $('.payment-item__content').hide();
      $(this).closest('.payment-item').find('.payment-item__content').show();
  });
  // ========================== Checkout Payment Method Js End ================================

  
  // ================== Password Show Hide Js Start ==========
  $(".toggle-password").on('click', function() {
    $(this).toggleClass("active");
    var input = $($(this).attr("id"));
    if (input.attr("type") == "password") {
      input.attr("type", "text");
    } else {
      input.attr("type", "password");
    }
  });
  // ========================= Password Show Hide Js End ===========================
  

  });
  // ==========================================
  //      End Document Ready function
  // ==========================================

  // ========================= Preloader Js Start =====================
    $(window).on("load", function(){
      $('.preloader').fadeOut(); 
    })
    // ========================= Preloader Js End=====================

    // ========================= Header Sticky Js Start ==============
    $(window).on('scroll', function() {
      if ($(window).scrollTop() >= 260) {
        $('.header').addClass('fixed-header');
      }
      else {
          $('.header').removeClass('fixed-header');
      }
    }); 
    // ========================= Header Sticky Js End===================

})(jQuery);
