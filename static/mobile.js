Store = function(str) {
	return {
		get: function() {
			return JSON.parse(localStorage[str]);
		},
		set: function(val) {
			localStorage[str] = JSON.stringify(val);
			return val;
		},
		get exists() {
			return typeof localStorage[str] !== "undefined";
		},
        destroy: function() {
            delete localStorage[str];                
        }   
	};
};

Array.prototype.shuffle = function() {
  var b, i, item, _len, _ref;
  for (i = 0, _len = this.length; i < _len; i++) {
    item = this[i];
    b = Math.floor(Math.random() * (i + 1));
    _ref = [this[b], this[i]], this[i] = _ref[0], this[b] = _ref[1];
    i++;
  }
  return this;
};

window.map = {
	"v": "Verb",
	"n": "Noun",
	"adj": "Adjective",
	"adv": "Adverb",
	"prep": "Preposition",
	"interj": "Interjection"
};


App = function() {
	this.el = $(".container");
	
	this.width = $(window).width();
	
	this.list = [];
	
	this.currentCard = {};
	
	this.outerMarkup = $("#template").html()
	this.innerMarkup = $(this.outerMarkup).html()
	
	this.nextCard = function() {

		if (this.currentCard) this.list.splice(10, 0, this.currentCard);
		
		this.card.css({ left: -1000 });
		
		var obj = this.list.shift();
		if (typeof obj.w == "undefined") obj = this.list.shift();
		
		while (obj.w in app.knowit.get()) {
			console.log("skipped ", obj.w);
			obj = this.list.shift();
		}
		
		$.getJSON("http://cardmemoriae.appspot.com/dictionary/"+obj.w, function(data) {	
			this.currentCard = obj;
			obj.p = map[obj.p];
			obj.pro = data.pronunciation;
			obj.ex = data.example;
			this.card.html("");
			$.tmpl(this.innerMarkup, obj).appendTo(this.card);
			this.card.css({ left: ($(window).width()-600)/2 });
			
		}.bind(this));
	
	};
	
	this.doknowit = function() {
		var obj = app.knowit.get();
		obj[this.currentCard.w] = "";
		app.knowit.set(obj);
		this.currentCard = false;
		this.nextCard();
	};
	
	this.ready = function() {
			this.list = app.list.get().shuffle();
			this.card = $.tmpl(this.outerMarkup, null).css("display", "block").appendTo(this.el);
			this.card.css('left', ( $(window).width() - 600 ) / 2 );
			this.card.bind("click", function() {
				$(this).toggleClass("flipped");
			});
			this.card.swipe({
				right: function() {
					this.nextCard();
				}
			});
			this.nextCard();
	};

	this.initialize = function() {
		if (!app.knowit.exists) {
			app.knowit.set({});
		}
		if (!app.list.exists) {
			$.getJSON("list.json", function(data) {
				app.list.set(data);
				this.ready();
			}.bind(this));
		}
		else {
			this.ready();
		}
	};
	
};


$(function(){

	window.app = new App;
	
	app.knowit = new Store("knowit");
	app.list = new Store("list");
	
	app.initialize();

});



