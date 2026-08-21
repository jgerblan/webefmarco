var _____WB$wombat$assign$function_____=function(name){return (globalThis._wb_wombat && globalThis._wb_wombat.local_init && globalThis._wb_wombat.local_init(name))||globalThis[name];};if(!globalThis.__WB_pmw){globalThis.__WB_pmw=function(obj){this.__WB_source=obj;return this;}}{
let window = _____WB$wombat$assign$function_____("window");
let self = _____WB$wombat$assign$function_____("self");
let document = _____WB$wombat$assign$function_____("document");
let location = _____WB$wombat$assign$function_____("location");
let top = _____WB$wombat$assign$function_____("top");
let parent = _____WB$wombat$assign$function_____("parent");
let frames = _____WB$wombat$assign$function_____("frames");
let opener = _____WB$wombat$assign$function_____("opener");
/** 
 *------------------------------------------------------------------------------
 * @package       T3 Framework for Joomla!
 *------------------------------------------------------------------------------
 * @copyright     Copyright (C) 2004-2013 JoomlArt.com. All Rights Reserved.
 * @license       GNU General Public License version 2 or later; see LICENSE.txt
 * @authors       JoomlArt, JoomlaBamboo, (contribute to this project at github 
 *                & Google group to become co-author)
 * @Google group: https://groups.google.com/forum/#!forum/t3fw
 * @Link:         http://t3-framework.org 
 *------------------------------------------------------------------------------
 */

!function($){

  // legacy for $.browser to detect IE
  if ($.browser == undefined || $.browser.msie == undefined) {
    $.browser={msie:false,version:0};
    if (match = navigator.userAgent.match (/MSIE ([0-9]{1,}[\.0-9]{0,})/) || navigator.userAgent.match (/Trident.*rv:([0-9]{1,}[\.0-9]{0,})/)) {
      $.browser.msie=true;
      $.browser.version=match[1];
    }
  }
	// add ie version to html tag
  if ($.browser.msie) {
    $('html').addClass('ie'+ Math.floor($.browser.version));
  }

	// Detect grid-float-breakpoint value and put to $(body) data
	$(document).ready(function(){
			if (!window.getComputedStyle) {
					window.getComputedStyle = function(el, pseudo) {
							this.el = el;
							this.getPropertyValue = function(prop) {
									var re = /(\-([a-z]){1})/g;
									if (prop == 'float') prop = 'styleFloat';
									if (re.test(prop)) {
											prop = prop.replace(re, function () {
													return arguments[2].toUpperCase();
											});
									}
									return el.currentStyle[prop] ? el.currentStyle[prop] : null;
							}
							return this;
					}
			}
			var fromClass = 'body-data-holder',
					prop = 'content',
					$inspector = $('<div>').css('display', 'none').addClass(fromClass).appendTo($('body'));

			try {
					var attrs = window.getComputedStyle(
							$inspector[0], ':before'
					).getPropertyValue(prop);
					if(attrs){
							var matches = attrs.match(/([\da-z\-]+)/gi),
									data = {};
							if (matches && matches.length) {
									for (var i=0; i<matches.length; i++) {
											data[matches[i++]] = i<matches.length ? matches[i] : null;
									}
							}
							$('body').data (data);
					}
			} finally {
					$inspector.remove(); // and remove from DOM
			}
	});
	
	
	//detect transform (https://github.com/cubiq/)
	(function(){
		$.support.t3transform = (function () {
			var style = document.createElement('div').style,
			vendors = ['t', 'webkitT', 'MozT', 'msT', 'OT'],
			transform, i = 0, l = vendors.length;

			for ( ; i < l; i++ ) {
				transform = vendors[i] + 'ransform';
				if ( transform in style ) {
					return transform;
				}
			}

			return false;
		})();

	})();
	
	//basic detect touch
	(function(){
		$('html').addClass('ontouchstart' in window ? 'touch' : 'no-touch');
	})();
	
	//document ready
	$(document).ready(function(){

		//remove conflict of mootools more show/hide function of element
		(function(){
			if(window.MooTools && window.MooTools.More && Element && Element.implement){

				var mthide = Element.prototype.hide,
					mtshow = Element.prototype.show,
					mtslide = Element.prototype.slide;

				Element.implement({
					show: function(args){
						if(arguments.callee &&
							arguments.callee.caller &&
							arguments.callee.caller.toString().indexOf('isPropagationStopped') !== -1){	//jquery mark
							return this;
						}

						return $.isFunction(mtshow) && mtshow.apply(this, args);
					},

					hide: function(){
						if(arguments.callee &&
							arguments.callee.caller &&
							arguments.callee.caller.toString().indexOf('isPropagationStopped') !== -1){	//jquery mark
							return this;
						}

						return $.isFunction(mthide) && mthide.apply(this, arguments);
					},

					slide: function(args){
						if(arguments.callee &&
							arguments.callee.caller &&
							arguments.callee.caller.toString().indexOf('isPropagationStopped') !== -1){	//jquery mark
							return this;
						}

						return $.isFunction(mtslide) && mtslide.apply(this, args);
					}
				})
			}
		})();

		// overwrite default tooltip/popover behavior (same as Joomla 3.1.5)
		$.fn.tooltip.Constructor && $.fn.tooltip.Constructor.DEFAULTS && ($.fn.tooltip.Constructor.DEFAULTS.html = true);
		$.fn.popover.Constructor && $.fn.popover.Constructor.DEFAULTS && ($.fn.popover.Constructor.DEFAULTS.html = true);
		$.fn.tooltip.defaults && ($.fn.tooltip.defaults.html = true);
		$.fn.popover.defaults && ($.fn.popover.defaults.html = true);

		//fix JomSocial navbar-collapse toggle
		(function(){
			if(window.jomsQuery && jomsQuery.fn.collapse){
			
				$('[data-toggle="collapse"]').on('click', function(e){
					
					//toggle manual
					$($(this).attr('data-target')).eq(0).collapse('toggle');
					
					//stop
					e.stopPropagation();

					return false;
				});

				//remove conflict on touch screen
				jomsQuery('html, body').off('touchstart.dropdown.data-api');
			}	
		})();


		//fix chosen select
		(function(){
			if($.fn.chosen && $(document.documentElement).attr('dir') == 'rtl'){
				$('select').addClass('chzn-rtl');
			}	
		})();

	});

	$(window).load(function(){

		//fix animation for navbar-collapse-fixed-top||bottom
		if(!$(document.documentElement).hasClass('off-canvas-ready') &&
			($('.navbar-collapse-fixed-top').length ||
			$('.navbar-collapse-fixed-bottom').length)){

			var btn = $('.btn-navbar[data-toggle="collapse"]');
			if (!btn.length){
				return;
			}

			if(btn.data('target')){
				var nav = $(btn.data('target'));
				if(!nav.length){
					return;
				}

				var fixedtop = nav.closest('.navbar-collapse-fixed-top').length;

				btn.on('click', function(){

					var wheight = (window.innerHeight || $(window).height());

					if(!$.support.transition){
						nav.parent().css('height', !btn.hasClass('collapsed') && btn.data('t3-clicked') ? '' : wheight);
						btn.data('t3-clicked', 1);
					}

					nav
						.addClass('animate')
						.css('max-height', wheight -
							(fixedtop ? (parseFloat(nav.css('top')) || 0) : (parseFloat(nav.css('bottom')) || 0)));
				});
				nav.on('shown hidden', function(){
					nav.removeClass('animate');
				});
			}
		}

	});

}(jQuery);
}

/*
     FILE ARCHIVED ON 07:56:12 Jun 15, 2024 AND RETRIEVED FROM THE
     INTERNET ARCHIVE ON 15:14:41 Aug 21, 2026.
     JAVASCRIPT APPENDED BY WAYBACK MACHINE, COPYRIGHT INTERNET ARCHIVE.

     ALL OTHER CONTENT MAY ALSO BE PROTECTED BY COPYRIGHT (17 U.S.C.
     SECTION 108(a)(3)).
*/
/*
playback timings (ms):
  captures_list: 0.563
  exclusion.robots: 0.07
  exclusion.robots.policy: 0.059
  esindex: 0.007
  cdx.remote: 6.845
  LoadShardBlock: 101.212 (3)
  PetaboxLoader3.resolve: 313.751 (4)
  PetaboxLoader3.datanode: 63.336 (5)
  load_resource: 282.732
  loaddict: 15.406
*/