
function add_word(word_info) {
   var WORD_SPACE  = 1;
   var WORD_IGNORED = 2;
   var WORD_ANNOTATED = 3;
   var WORD_PARAGRAPH = 4;
   
   var parent_elem = $('<span />').appendTo('.main_panel');
   var text_elem = $('<a />').appendTo($(parent_elem));
   var word_class = word_info['class'];
   if (word_class == WORD_SPACE) {
	  $(text_elem).text(' ');
   }
   else if (word_class == WORD_ANNOTATED) {
	   var word = word_info['text']
	   
	   var definition = word_info['def'];
	   var content = '<span class="popup_defined_word">' + word + '</span><br>' + 
	                 '<span class="popup_definition">' + definition + '</span>';
	   
	   $(text_elem).text(word);
	   if(definition.length > 0) {
	       $(text_elem).addClass("defined_word");
	       $(text_elem).tooltipster({
                content :  $(content),
				trigger : 'click',
				theme : 'tooltipster-light',
				position : 'bottom',
				speed : 150,
				delay : 0,
				onlyOne : true
            });
	   }
	   else {
			$(text_elem).addClass("word_without_definition");
	   }
   }
   else if (word_class == WORD_IGNORED) {
	   $(text_elem).text(word_info['text']);
   }
   else if (word_class == WORD_PARAGRAPH) {
   	   $(parent_elem).html('<br>');
   }
   else {
	   console.log('Unknown word class: ' + word_class.toString());
   }
}

function annotate(text_obj) {

   //#var text_elem = $('body').append('div');
   //$(text_elem).text('ttt');
   $.each( text_obj, 
           function(index, value) {
				add_word(value)
           }
   );
}