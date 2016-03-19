
function annotate_word(word_info) {
   var WORD_SPACE  = 1;
   var WORD_IGNORED = 2;
   var WORD_ANNOTATED = 3;
   var WORD_PARAGRAPH = 4;
   
   var parent_elem = $('<span />').appendTo('.main_panel');
   var text_elem = $(parent_elem);
   var word_class = word_info['class'];
   if (word_class == WORD_SPACE) {
	  $(text_elem).text(' ');
   }
   else if (word_class == WORD_ANNOTATED) {
       var word = word_info['text']
       $(text_elem).text(word);
	   attach_tooltip(text_elem, word_info)
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

function attach_tooltip(text_elem, word_info) {
   $(text_elem).addClass("defined_word");
   $(text_elem).tooltipster({
		content : 'Loading...',
		functionBefore: function(origin, continueTooltip) { 
						  //if (origin.data('ajax') !== 'cached') {
						   var content = create_tooltip_content(word_info);
						   origin.tooltipster('content', content).data('ajax', 'cached');
						   continueTooltip();
						},
		trigger : 'click',
		theme : 'tooltipster-light',
		position : 'bottom',
		interactive : true,
		speed : 150,
		delay : 0,
		onlyOne : true
	});
}

function create_tooltip_content(word_info) {
   var word = word_info['text']
   var dictionary_form = word_info['dict_form'] ? word_info['dict_form'] : word;
   var definition = global_glossary[dictionary_form] ? global_glossary[dictionary_form] : '';
   var part_of_speech = word_info['pos'];
   var part_of_speech_info = '';
   if(part_of_speech) {
	  part_of_speech_info = '&nbsp;<span class="popup_part_of_speech">(' + part_of_speech + ')</span>';
   }
   
   var content = '<span class="popup_defined_word">' + dictionary_form + '</span>';
   content += part_of_speech_info;
   content += '<br>';
   
   definition_split = '';
   definition.split('\n').forEach( function(value, index) {
		definition_split += value + '<br>';
   } );
   content += '<span class="popup_definition">' + definition_split + '</span>';
   return $(content);
}

function annotate(text_obj) {
   $.each( text_obj, 
           function(index, value) {
				annotate_word(value)
           }
   );
}