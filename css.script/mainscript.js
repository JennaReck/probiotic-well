$(document).ready(function() {
	var containerWidth;
	var slideAmount;

	function slideLeft(containerID) {
		containerWidth = $('.slider-container').width();
		slideAmount = containerWidth - $('.slider-product-container').css("marginLeft").replace('px', '');
		if ($(containerID).position().left + 
				$(containerID).width() - slideAmount > 
				slideAmount) {
			$(containerID).animate(
				{left:"-="+slideAmount+"px"}, 
				{duration:'slow',
				easing:'swing'
				});
		}
		else {
			pos = $(containerID).width() - slideAmount;
			$(containerID).animate(
				{left:"-"+pos+"px"}, 
				{duration:'slow',
				easing:'swing'
				});
		}
	}

	function slideRight(containerID) {
		containerWidth = $('.slider-container').width();
				slideAmount = containerWidth - $('.slider-product-container').css("marginLeft").replace('px', '');
				if ($(containerID).position().left + slideAmount < 0) {
						$(containerID).animate(
							{left:"+="+slideAmount+"px"}, 
							{duration:'slow',
							easing:'swing'
						});
					}
				else {
					$(containerID).animate(
							{left:"0px"}, 
							{duration:'slow',
							 easing:'swing'
							});
				}
	}

	$('#slider-brands-arrow-right').click(function(){
		slideLeft('#slider-brands-overflow-container');
		});


	$('#slider-brands-arrow-left').click (function() {
		slideRight('#slider-brands-overflow-container');
		});
	  
	  
	$('#slider-reviews-arrow-right').click(function() {
		slideLeft('#slider-reviews-overflow-container');
	});


	$('#slider-reviews-arrow-left').click (function() {
		slideRight('#slider-reviews-overflow-container');
	});
	

});

/* INDIVIDUAL ARTICLE PAGE SCRIPT */
function toggleEmailForm() {
	$('#article-email-form-container').toggleClass('hidden article-email-form-container');
	$('#email-from').val('');
	$('#email-to').val('');
	$('#email-message').val('');
	$('#email-error-success-message').html('');
	};
	
function toggleSubscribeForm() {
	$('#subscribe-form-container').toggleClass('hidden article-email-form-container');
	$('#subscribe-articles').attr('checked', false);
	$('#subscribe-reviews').attr('checked', false);
	$('#subscribe-sales').attr('checked', false);
	$('#subscribe-error-success-message').html('');
	};
	
function checkSubscribeForm() {
	email = $('#subscribe-email').val();
	articles = $('#subscribe-articles').prop("checked");
	reviews = $('#subscribe-reviews').prop("checked");
	sales = $('#subscribe-sales').prop("checked");
	unsubscribed = $('#unsubscribe').prop("checked");
	error = "";
	if (!email.match(/@[^\r\n]*\./) && (articles || reviews || sales || unsubscribed)) {
		error = "Email is invalid. Please enter a valid email.";
	}
	else if (!email.match(/@[^\r\n]*\./) && !articles && !reviews && !sales && !unsubscribed) {
		error = "Email is invalid. Please enter a valid email.<br />Please check one or more boxes.";
	}
	else if (!articles && !reviews && !sales && !unsubscribed) {
		error = "Please check one or more boxes.";
	}
	else {
		return true;
	}
	if ($( '#subscribe-error-success-message' ).hasClass( 'success' ) ) {
			$( '#subscribe-error-success-message' ).toggleClass( 'success error' );
		}
	$('#subscribe-error-success-message').html(error);
	return false;
};

function checkEmailForm() {
	fromEmail = $('#email-from').val();
	toEmail = $('#email-to').val();
	message = $('#email-message').val();
	error = "";
	if (!fromEmail.match(/@[^\r\n]*\./) && toEmail.match(/@[^\r\n]*\./)) {
		error = "From email is invalid. Please enter a valid email.";
	}
	else if (!fromEmail.match(/@[^\r\n]*\./) && !toEmail.match(/@[^\r\n]*\./)) {
		error = "From email is invalid. To email is invalid.<br />Please enter a valid email.";
	}
	else if (fromEmail.match(/@[^\r\n]*\./) && !toEmail.match(/@[^\r\n]*\./)) {
		error = "To email is invalid. Please enter a valid email.";
	}
	else {
		return true;
	}
	if ($( '#email-error-success-message' ).hasClass( 'success' ) ) {
			$( '#email-error-success-message' ).toggleClass( 'success error' );
		}
	$('#email-error-success-message').html(error);
	return false;
};
	
function checkContactForm() {
	from = $('#contact-from').val();
	message = $('#contact-message').val();
	error = "";
	if (!from.match(/@[^\r\n]*\./) && message == "") {
		error = "Email is invalid. Please enter a valid email.<br />Question or comment is blank. Please enter a message.";
	}
	else if (!from.match(/@[^\r\n]*\./)) {
		error = "Email is invalid. Please enter a valid email.";
	}
	else if (message == "") {
		error = "Question or comment is blank. Please enter a message.";
	}
	else {
		return true;
	}
	$('#contact-error').html(error);
	return false;
};
	
function sendEmailForm() {
	check = checkEmailForm();
	if (check) {
		emailFrom = $('#email-from').val();
		emailTo = $('#email-to').val();
		message = $('#email-message').val();
		articleID = window.location.pathname.split('/')[2];
		targetURL = "http://probioticwell.appspot.com/pass-email" + "?from=" + 
					emailFrom + "&to=" + emailTo + "&message=" + message +
					"&article-id=" + articleID;
		jQuery.post(targetURL);
		$('#email-from').val('');
		$('#email-to').val('');
		$('#email-message').val('');
		if ($( '#email-error-success-message' ).hasClass( 'error' ) ) {
			$( '#email-error-success-message' ).toggleClass( 'error success' );
		}
		$('#email-error-success-message').html('<p>Success! Thanks for sharing this article!</p><a class="center-text main-links" href="javascript:toggleEmailForm()">close window</a>');
	}
};

function sendSubscribeForm() {
	check = checkSubscribeForm();
	if (check) {
		email = $('#subscribe-email').val();
		articles = $('#subscribe-articles').prop("checked");
		reviews = $('#subscribe-reviews').prop("checked");
		sales = $('#subscribe-sales').prop("checked");
		
		targetURL = "http://probioticwell.appspot.com/email-alert-settings" + 
					"?subscribe-email=" + email + "&subscribe-articles=" +
					articles + "&subscribe-reviews=" + reviews +
					"&subscribe-sales=" + sales + "&unsubscribe=undefined";
		jQuery.post(targetURL);
		$('#subscribe-email').val('');
		$('#subscribe-articles').attr('checked', false);
		$('#subscribe-reviews').attr('checked', false);
		$('#subscribe-sales').attr('checked', false);
		if ($( '#subscribe-error-success-message' ).hasClass( 'error' ) ) {
			$( '#subscribe-error-success-message' ).toggleClass( 'error success' );
		}
		$('#subscribe-error-success-message').html('<p>Success! Thanks for subscribing!</p><a class="center-text main-links" href="javascript:toggleSubscribeForm()">close window</a>');
	}
	else {
		return false;
	}
};

function toggleCitations() {
	$('#citations-container').toggleClass('hidden shown');
	if ($('#citation-button').text() == "show") {
		$('#citation-button').text("hide");
	}
	else {
		$('#citation-button').text("show");
	}
};

function showCitation(citationNumber) {
	if ($('#citations-container').hasClass('hidden') ) {
		$('#citations-container').attr('class', 'shown');
		$('#citation-button').text("hide");
	}
	$(location).attr('hash', "");
	$(location).attr('hash', citationNumber);
};

function getRank() {
	productID = $('#product-id').val();
	targetURL = "http://probioticwell.appspot.com/get-rank" + "?product-id=" + productID;
	jQuery.get(targetURL, function( data ) {
		$('#rank-result').val(data);
	});
};