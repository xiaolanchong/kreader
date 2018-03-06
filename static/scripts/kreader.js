
function annotate_word(word_info, theme_class) {
   var WORD_SPACE  = 1;
   var WORD_IGNORED = 2;
   var WORD_ANNOTATED = 3;
   var WORD_PARAGRAPH = 4;
   
   var parent_elem = $('<span />').appendTo('.text-body');
   var text_elem = $(parent_elem);
   var word_class = word_info['class'];
   if (word_class == WORD_SPACE) {
     $(text_elem).text(' ');
   }
   else if (word_class == WORD_ANNOTATED) {
       var word = word_info['text']
       $(text_elem).text(word);
      attach_tooltip(text_elem, word_info, theme_class)
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

function attach_tooltip(text_elem, word_info, theme_class) {
   $(text_elem).addClass("defined_word");
   $(text_elem).tooltipster({
      content : 'Loading...',
      functionBefore: function(origin, continueTooltip) { 
                     if (false) {
                      var content = create_tooltip_content_onplace(word_info, text_elem);
                      origin
					     .tooltipster('content', content)
						 .data('ajax', 'cached')
						 .addClass(theme_class);
                     } else {
                        request_definition(origin, word_info, text_elem);
                     }
                     
                     continueTooltip();
                  },
      trigger : 'click',
      theme : 'tooltipster-default',
      position : 'bottom',
      interactive : true,
      speed : 0,
      delay : 0,
      onlyOne : true
   });
}

function request_definition(origin, word_info, clicked_elem) {
   var word = word_info['text']
   var dictionary_form = word_info['dict_form'] || word;
   $.ajax({ url: '/definition/' + dictionary_form, 
       data: {},
       success: function(data){
         var definitions = data["definitions"] || [];
         var content = create_tooltip_content_async(word_info, definitions, clicked_elem);
         origin.tooltipster('content', content).data('ajax', 'cached');
       }, 
       error: function(req) { 
			origin.tooltipster('content', 'Error occuried'); 
		},
       dataType: "json"
	   });
}

function create_tooltip_content_async(word_info, definitions, clicked_elem){
   
   var word = word_info['text']
   var dictionary_form = word_info['dict_form'] || word;
   var dependent_tokens = word_info['dec_tok'] || [];

   conjugation_info = ''
   $.each(dependent_tokens, function(index, value) {
      conjugation_info += ' +' + value[1]; // + '/' + value[0];
   });

   var part_of_speech = word_info['pos'];
   return create_tooltip_content(dictionary_form, definitions, 
                    part_of_speech, conjugation_info, clicked_elem);
}

function create_tooltip_content_onplace(word_info, clicked_elem) {
   var word = word_info['text']
   var dictionary_form = word_info['dict_form'] || word;
   var definitions = global_glossary[dictionary_form] || [];
   var part_of_speech = word_info['pos'];
   return create_tooltip_content(dictionary_form, definitions, part_of_speech, '', clicked_elem);
}

function create_tooltip_content(dictionary_form, definitions, 
              part_of_speech, conjugation_info, clicked_elem) {
   var part_of_speech_info = '';
   if(part_of_speech) {
     part_of_speech_info = '&nbsp;<span class="popup_part_of_speech">(' + part_of_speech + ')</span>';
   }
   
   var content = '';
   content += '<span class="popup_defined_word">' + dictionary_form + '</span>';
   content += part_of_speech_info;
   content += '<span class="popup_conjugation_info">' + conjugation_info + '</span>';
   content += '<br>';
   
   definition_split = '<ul>';
   definitions.forEach( function(definition, index) {
      if (definition.length > 0) {
         definition_split += '<li>'
         definition.split('\n').forEach( function(value, index) {
            definition_split += value + '<br>';
         } );
         definition_split += '</li>'
      }
   });
   definition_split += '</ul>';
   
   content += '<span class="popup_definition">' + definition_split + '</span>';
  
  /* sound off  
   pronunciation_url = "/sound/" + dictionary_form;
   content += '<div class="popup_pronounce_button"><a id="play_button" href="#">' + 
              '<img src="static/images/Sound2.png"></img><a></div>';
   content += '<audio id="player"><source src="' + pronunciation_url + '"  preload="none"/></audio>'
  */
   content += '<div class="popup_add_word_button"><a id="add_word_button" href="#">' + 
              '<img src="static/images/Add.png"></img><a></div>';  
   var new_elem = $(content);
  /* sound off   
   $("#play_button", new_elem).click(function() {
             $('#player').get(0).play();
             return false;
         });
  */
   $("#add_word_button", new_elem).click(function() {
			 var context = extract_context(clicked_elem);
			 add_new_word(dictionary_form, context);
             return false;
         });  

   return new_elem;
}

function add_new_word(word, context) {
   $.ajax({ url: '/new_word/' + word, 
       data: { 'context': context, 'text_id': current_text_id},
	   method: 'PUT', 
       success: function(data){
         
       }, 
       error: function(req) { /* TODO: error msge */ }
	   });		
}

function delete_new_word(word, word_id) {
   $.ajax({ url: '/new_word/' + word, 
       data: { 'word_id': word_id},
	   method: 'DELETE', 
       success: function(data){
         
       }, 
       error: function(req) { /* TODO: error msge */ }
	   });		
}

function annotate(text_obj) {
   $.each( text_obj, 
           function(index, value) {
            annotate_word(value)
           }
   );
}

function send_font_settings(font_size) {
	data = {'font_size' : font_size };
	send_settings(data);
}

function change_text_size(delta) {
   var font_size = $( "#settings-font-size" ).val();
   font_size = parseFloat(font_size);
   var new_font_size = Math.min(25, Math.max(5, font_size + delta));
   if(Math.abs(font_size - new_font_size) > 1e-3) {
       $( "#settings-font-size" ).val('' + new_font_size);
	   $( "#settings-font-sample" ).css('font-size', new_font_size);
	   send_font_settings(new_font_size);
   }
}

function change_theme(theme) {
	data = {'theme' : theme };
	send_settings(data);
}

function send_settings(data) {
   $.ajax({ url: '/settings', 
       data: data,
	   method: 'PUT', 
       success: function(data){
         
       }, 
       error: function(req) { /* TODO: error msge */ }
	   });	
}

function init_settings(font_size, theme) {
	
   $( "#settings-font-size" ).val('' + font_size);
   $( "#settings-font-sample" ).css('font-size', font_size);
	   
   $( "#settings-font-dec" )
       .click(function() {
            change_text_size(-1);
   }); 
   
   $( "#settings-font-inc")
      .click(function() {
            change_text_size(1);
   });
   
   $( "#settings-theme-light")
      .prop("checked", theme == "light")
      .click(function() {
            change_theme('light');
   });
   
   $( "#settings-theme-dark")
      .prop("checked", theme == "dark")
      .click(function() {
            change_theme('dark');
   });   

   $( "#settings-theme-sepia")
      .prop("checked", theme == "sepia")
      .click(function() {
            change_theme('sepia');
   });

}

function delete_text(text_id) {
   $.ajax({ url: '/text/' + text_id, 
       data: {},
	   method: 'DELETE', 
       success: function(data){
         
       }, 
       error: function(req) { /* TODO: error msg */ }
	   });	
}

function concat(one, two, forward) {
	return forward ? one + two : two + one;
}

function get_side_context(elem, forward) {
	const stop_symbol_re = /([\.!\?])/ig;
	const max_length = 100;
	let result = '';
	let iteration_round = 0;
	while((forward ? $(elem).next() : $(elem).prev()).length) {
		if(iteration_round > 150) {
			console.error("Context loop halted");
			break;
		}
		elem = forward ? $(elem).next() : $(elem).prev();	
		let text = $(elem).text();
		if (text.length + result.length <= max_length) {
		//	console.log('Added symbols: ' + text + ', ' + result.length);
			result = concat(result, text, forward);
		}
		else {
			let match_res = stop_symbol_re.exec(text);
			if(match_res != null && match_res.index >= 0) {
				result = concat(result, text.substring(0, match_res.index + (forward? 1 : 0)), forward);
		//		console.log('Found stop symbol in ' + text + ', ' + match_res.index + ', ' + result.length);
				break;
			}
			else if(result.length < 2*max_length) {
				result = concat(result, text, forward);
		//		console.log('Added symbols after limit: ' + text + ', ' + result.length);
			}
			else {
				
			}
		}
		iteration_round += 1;
	}
	return result;
}

// Extracts a sentence or two from the text, which the current html element belongs to
function extract_context(elem) {
	let ahead_context = get_side_context(elem, true);
	let behind_context = get_side_context(elem, false);
	let result = behind_context + $(elem).text() + ahead_context;
	//console.log(result);
	return result;
}
