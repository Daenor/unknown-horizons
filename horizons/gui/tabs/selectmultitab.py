# ###################################################
# Copyright (C) 2011 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

from tabinterface import TabInterface
from horizons.util import Callback
from horizons.util.gui import load_uh_widget

class SelectMultiTab(TabInterface):
	"""
	Tab shown when multiple units are selected
	"""
	def __init__(self, session = None, widget = 'overview_select_multi.xml', \
	             icon_path='content/gui/icons/tabwidget/common/inventory_%s.png'):
		super(SelectMultiTab, self).__init__(widget = widget)
		self.session = session
		self.init_values()

		self.button_up_image = icon_path % 'u'
		self.button_active_image = icon_path % 'a'
		self.button_down_image = icon_path % 'd'
		self.button_hover_image = icon_path % 'h'

		# keep track of units that have stance
		self.stance_units = []
		# keep track of units that don't have a stance
		self.non_stance_units = []
		# if the stance units are no longer selected hide the stance menu

		self.tooltip = _("Selected Units")
		for i in self.session.selected_instances:
			if hasattr(i, 'stance'):
				self.stance_units.append(i)
			else:
				self.non_stance_units.append(i)

		if self.stance_units:
			self.show_stance_widget()

	def get_tab_units(self):
		"""
		Returns list of units shown in the tab
		"""
		return self.stance_units + self.non_stance_units

	def show(self):
		super(SelectMultiTab, self).show()
		for i in self.get_tab_units():
			if not i.has_remove_listener(Callback(self.on_instance_removed, i)):
				i.add_remove_listener(Callback(self.on_instance_removed, i))

	def hide(self):
		super(SelectMultiTab, self).hide()
		for i in self.get_tab_units():
			if i.has_remove_listener(Callback(self.on_instance_removed, i)):
				i.remove_remove_listener(Callback(self.on_instance_removed, i))

	def on_instance_removed(self, instance):
		if instance.has_remove_listener(Callback(self.on_instance_removed, instance)):
			instance.remove_remove_listener(Callback(self.on_instance_removed, instance))
		if hasattr(instance, 'stance'):
			self.stance_units.remove(instance)
		else:
			self.non_stance_units.remove(instance)
		if not self.stance_units:
			self.hide_stance_widget()

	def show_stance_widget(self):
		stance_widget = load_uh_widget('stancewidget.xml')
		self.widget.findChild(name='stance').addChild(stance_widget)
		self.toggle_stance()
		self.widget.mapEvents({
			'aggressive': Callback(self.set_stance, 'aggressive'),
			'hold_ground': Callback(self.set_stance, 'hold_ground'),
			'none': Callback(self.set_stance, 'none'),
			'flee': Callback(self.set_stance, 'flee')
		})

	def hide_stance_widget(self):
		self.widget.findChild(name='stance').removeAllChildren()

	def set_stance(self, stance):
		for i in self.stance_units:
			i.set_stance(stance)
		self.toggle_stance()

	def toggle_stance(self):
		"""
		Toggles the stance, Assumes at least one stance unit is selected
		"""
		self.widget.findChild(name='aggressive').set_inactive()
		self.widget.findChild(name='hold_ground').set_inactive()
		self.widget.findChild(name='none').set_inactive()
		self.widget.findChild(name='flee').set_inactive()
		# get first unit stance
		stance = self.stance_units[0].stance
		for unit in self.stance_units[1:]:
			if unit.stance != stance:
				return
		self.widget.findChild(name = stance).set_active()
				
