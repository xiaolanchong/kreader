
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
                     if (false) {
                      var content = create_tooltip_content_onplace(word_info);
                      origin.tooltipster('content', content).data('ajax', 'cached');
                     } else {
                        request_definition(origin, word_info);
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

function request_definition(origin, word_info) {
   var word = word_info['text']
   var dictionary_form = word_info['dict_form'] || word;
   $.ajax({ url: '/definition/' + dictionary_form, 
       data: {},
       success: function(data){
         var definitions = data["definitions"] || [];
         var content = create_tooltip_content_async(word_info, definitions);
         origin.tooltipster('content', content).data('ajax', 'cached');
       }, 
       error: function(req) { origin.tooltipster('content', 'Error occuried'); },
       dataType: "json"});
}

function create_tooltip_content_async(word_info, definitions){
   
   var word = word_info['text']
   var dictionary_form = word_info['dict_form'] || word;
   var dependent_tokens = word_info['dec_tok'] || [];

   conjugation_info = ''
   $.each(dependent_tokens, function(index, value) {
      conjugation_info += ' +' + value[1]; // + '/' + value[0];
   });

   var part_of_speech = word_info['pos'];
   return create_tooltip_content(dictionary_form, definitions, 
                    part_of_speech, conjugation_info);
}

function create_tooltip_content_onplace(word_info) {
   var word = word_info['text']
   var dictionary_form = word_info['dict_form'] || word;
   var definitions = global_glossary[dictionary_form] || [];
   var part_of_speech = word_info['pos'];
   return create_tooltip_content(dictionary_form, definitions, part_of_speech, '');
}

function create_tooltip_content(dictionary_form, definitions, 
              part_of_speech, conjugation_info) {
   var part_of_speech_info = '';
   if(part_of_speech) {
     part_of_speech_info = '&nbsp;<span class="popup_part_of_speech">(' + part_of_speech + ')</span>';
   }
   
   var content = '<span class="popup_defined_word">' + dictionary_form + '</span>';
   content += part_of_speech_info;
   content += '<span class="popup_conjugation_info">' + conjugation_info + '</span>';
   content += '<br>';
   
   definition_split = '<ul>';
   definitions.forEach( function(definition, index) {
      if (definition.length > 0) {
         definition_split += '<li>'
         //definition_split = '';
         definition.split('\n').forEach( function(value, index) {
            definition_split += value + '<br>';
         } );
         definition_split += '</li>'
      }
   });
   definition_split += '</ul>';
   
   content += '<span class="popup_definition">' + definition_split + '</span>';
   
   pronunciation_url = "/sound/" + dictionary_form;
   content += '<div class="popup_pronounce_button"><a id="play_button" href="#">' + 
              '<img src="static/images/Sound2.png"></img><a></div>';
   content += '<audio id="player"><source src="' + pronunciation_url + '"  preload="none"/></audio>'
  
   var new_elem = $(content);
   $("#play_button", new_elem).click(function() {
             $('#player').get(0).play();
             return false;
         });

   return new_elem;
}

function annotate(text_obj) {
   $.each( text_obj, 
           function(index, value) {
            annotate_word(value)
           }
   );
}

function change_text_size(delta) {
   var panel = $(".main_panel");
   var size = panel.css('font-size');
   var font_size = parseFloat(size);
   var new_font_size = Math.min(25, Math.max(5, font_size + delta));
   if(Math.abs(font_size - new_font_size) > 1e-3) {
     panel.css('font-size', new_font_size + 'px');
   }
}

function init_settings() {

var content_html = 
'<div id="settings_content">' +
'   <div >'  +
'      <div>Font Size:</div>'  +
'      <div>' +
'         <button id="settings-font-dec" style="">-</button>'  +
'         <button id="settings-font-inc" style="">+</button>'  +
'       </div>'  +
'      <div>Theme:</div>'  +
  '<form><div id="radio">' +
  '  <input type="radio" id="radio1" name="radio"><label for="radio1">Choice 1</label>' +
  '  <input type="radio" id="radio2" name="radio" checked="checked"><label for="radio2">Choice 2</label>' +
  '  <input type="radio" id="radio3" name="radio"><label for="radio3">Choice 3</label>' +
  '</div></form>' +
'</div>   ';

   var content_elem = $(content_html);
   $( "#settings-font-dec", content_elem )
       .button()
      .click(function() {
            change_text_size(-1);
            return false;
   }); 
   
   $( "#settings-font-inc", content_elem )
      .button()
     .click(function() {
            change_text_size(1);
            return false;
   });
   
   /*$( "#setting-light", content_elem ).button();
   $( "#setting-dark", content_elem ).button();
   $( "#setting-sepia", content_elem ).button();*/
   $( "#radio", content_elem ).buttonset();
  // $( "#radio1", content_elem ).attr('checked', true).button( "refresh" );
   

   $("#settings").tooltipster({
      content : content_elem,
      trigger : 'click',
      theme : 'tooltipster-light',
      position : 'bottom',
      interactive : true,
      speed : 150,
      delay : 0,
      onlyOne : true,
      //autoClose : false,
   });
}
