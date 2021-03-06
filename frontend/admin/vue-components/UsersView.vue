<template>
  <adminlte-box title="Users">
    <div class="alert alert-danger" v-if="communicationError">
      <strong>Error:</strong> {{communicationError}}
    </div>

    <data-table
    :headers.once="table.headers"
    :rows="table.rows"
    :globalActions="table.globalActions"
    :rowActions="table.rowActions">
    </data-table>
    <new-user-dialog
    v-if="newUserDialog.visible"
    :show="newUserDialog.visible"
    @created="newUserCreated"
    @closed="newUserDialog.visible = false;"></new-user-dialog>
    <confirm-dialog
    v-if="removeUserDialog.visible"
    :okCallback="removeUser"
    :closeCallback="closeRemoveUserDialog">
      <div>Do you want to remove User {{removeUserDialog.userToRemove.name}}
      ({{removeUserDialog.userToRemove.id}})</div>
    </confirm-dialog>
  </adminlte-box>
</template>

<script>
  let resources = require("admin-resources");
  let NewUserDialog = require("./users/NewUserDialog");

  module.exports = {
    components: {
      'new-user-dialog': NewUserDialog,
    },

    data: function () {
      return {
        table: {
          headers: ["ID", "Username"],
          rows: [],
          globalActions: [{
            label: "Create New Entry",
            callback: () => {this.newUserDialog.visible = true;}
          }],
          rowActions: [{
            label: "Policies",
            callback: this.showPolicyAction,
            type: "info"
          }, {
            label: "Remove",
            callback: this.removeAction
          }]
        },
        users: [],
        newUserDialog: {
          visible: false
        },
        removeUserDialog: {
          visible: false,
          userToRemove: {
            id: null,
            name: ""
          }
        },
        communicationError: null
      };
    },

    mounted: function () {
      this.updateTable();
    },

    methods: {
      updateTable: function() {
        this.communicationError = null;
        resources.User.items()
        .done((identifiers, items) => {
          this.table.rows = [];
          identifiers.forEach((id) => {
            let item = items[id];
            this.table.rows.push([
              id,
              item.name
            ]);
          });
        })
        .fail(() => {
          this.communicationError = "The request could not be executed successfully";
        });
      },

      newUserCreated: function() {
        this.newUserDialog.visible = false;
        this.updateTable();
      },

      showPolicyAction: function(row) {
        this.$router.push({
          name: 'user_accounting',
          params: { id: row[0] }
        });
      },

      removeAction: function(row) {
        this.removeUserDialog.userToRemove.id = row[0];
        this.removeUserDialog.userToRemove.name = row[1];
        this.removeUserDialog.visible = true;
      },

      closeRemoveUserDialog: function() {
        this.removeUserDialog.visible = false;
        this.removeUserDialog.userToRemove = {
          id: null,
          name: ""
        };
      },

      removeUser: function () {
        resources.User.delete(this.removeUserDialog.userToRemove.id)
        .done(() => {
          this.closeRemoveUserDialog();
          this.updateTable();
        })
        .fail(() => {
          this.closeRemoveUserDialog();
        });
      }
    }
  };
</script>
